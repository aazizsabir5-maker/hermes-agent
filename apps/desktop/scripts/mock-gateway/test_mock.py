#!/usr/bin/env python3
"""
Protocol test for the mock gateway — exercises the Setup-bot flow end to end
at the RPC/event level, plus the multi-process shared-state contract.

Run:  python3 scripts/mock-gateway/test_mock.py
"""

import json
import os
import re
import socket
import struct
import subprocess
import sys
import tempfile
import time

MOCK_DIR = os.path.dirname(os.path.abspath(__file__))
PORT = int(os.environ.get('MOCK_TEST_PORT', '8899'))
PORT2 = int(os.environ.get('MOCK_TEST_PORT2', '8900'))
STATE = os.path.join(tempfile.gettempdir(), 'mock-test-state.json')

# The shape of the real runbook's scripted asks — the mock quotes these back
# rather than keeping its own copy of the pills, so a seed without them is a
# guide with no fork. Two tiers here, which is what a new machine gets.
FORK_ASK = ('::ask{question="Know what you\'d like it to make?" '
            'options="Help me set up this Mac|Something else" input="true"}')
FALLBACK_ASK = ('::ask{question="What sounds better?" '
                'options="I have something in mind|Automate something I already do|'
                'Let\'s figure it out together|Skip this for now" input="true"}')
RUNBOOK = (
    'You are Setup, the persistent onboarding guide…\n'
    f'4. Then the fork: {FORK_ASK} alone as its own paragraph.\n'
    f'   If they pick "Something else": {FALLBACK_ASK} — same exactness rule.\n'
    'Interactive questions: end the message with ::ask{question="..." options="A|B|C"} alone.'
)


def _rm_state():
    for p in (STATE, STATE + '.tmp'):
        if os.path.exists(p):
            os.remove(p)


def ws_client(port, path='/api/ws?token=anything'):
    sock = socket.create_connection(('127.0.0.1', port))
    key = 'dGhlIHNhbXBsZSBub25jZQ=='
    req = (f'GET {path} HTTP/1.1\r\nHost: 127.0.0.1:{port}\r\n'
           'Upgrade: websocket\r\nConnection: Upgrade\r\n'
           f'Sec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n')
    sock.sendall(req.encode())
    buf = b''
    while b'\r\n\r\n' not in buf:
        buf += sock.recv(4096)
    return sock


def ws_send(sock, obj):
    payload = json.dumps(obj).encode()
    mask = b'\x01\x02\x03\x04'
    masked = bytes(c ^ mask[i % 4] for i, c in enumerate(payload))
    n = len(payload)
    hdr = bytes([0x81]) + (bytes([0x80 | n]) if n < 126 else bytes([0x80 | 126]) + struct.pack('>H', n))
    sock.sendall(hdr + mask + masked)


def ws_recv(sock, timeout=2.0):
    sock.settimeout(timeout)
    try:
        b1, b2 = sock.recv(2)
        ln = b2 & 0x7F
        if ln == 126:
            ln = struct.unpack('>H', sock.recv(2))[0]
        data = b''
        while len(data) < ln:
            data += sock.recv(ln - len(data))
        return json.loads(data.decode())
    except socket.timeout:
        return None


class Client:
    def __init__(self, port):
        self.sock = ws_client(port)
        self.seq = [0]

    def rpc(self, method, params=None, timeout=5.0):
        self.seq[0] += 1
        i = str(self.seq[0])
        ws_send(self.sock, {'jsonrpc': '2.0', 'id': i, 'method': method, 'params': params or {}})
        for _ in range(30):
            f = ws_recv(self.sock, timeout)
            if f and f.get('id') == i:
                if 'error' in f:
                    raise RuntimeError(f['error'].get('message', 'rpc error'))
                return f.get('result')
        raise TimeoutError(f'{method} timed out')

    def submit(self, sid, text, display_kind=None, timeout=30.0):
        params = {'session_id': sid, 'text': text}
        if display_kind:
            params['display_kind'] = display_kind
        self.seq[0] += 1
        i = str(self.seq[0])
        ws_send(self.sock, {'jsonrpc': '2.0', 'id': i, 'method': 'prompt.submit', 'params': params})
        # drain until the ack
        for _ in range(30):
            f = ws_recv(self.sock, timeout)
            if f and f.get('id') == i:
                break
        # then collect until message.complete for that session (if any reply)
        start = time.time()
        last = None
        while time.time() - start < 30:
            f = ws_recv(self.sock, 2.0)
            if not f:
                continue
            if f.get('method') == 'event':
                last = f['params'].get('type')
                if last == 'message.complete' and f['params'].get('session_id') == sid:
                    return f['params']['payload']['text']
                if last == 'session.info' and f['params'].get('session_id') == sid \
                        and f['params']['payload'].get('running') is False \
                        and time.time() - start > 2:
                    print(f'[submit] returning None after {last}, no complete for sid={sid}', file=sys.stderr)
                    return None  # no reply turn was scripted
        print(f'[submit] timed out after 30s, last event: {last}', file=sys.stderr)
        return None


def rest(port, path):
    import urllib.request
    with urllib.request.urlopen(f'http://127.0.0.1:{port}{path}', timeout=5) as r:
        return json.loads(r.read())


def start_server(port, profile):
    env = dict(os.environ, MOCK_PORT=str(port), HERMES_MOCK_STATE=STATE, MOCK_UNCONFIGURED_MS='0')
    proc = subprocess.Popen(
        [sys.executable, os.path.join(MOCK_DIR, 'mock_gateway.py'), '--profile', profile],
        env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
    )
    time.sleep(0.8)
    if proc.poll() is not None:
        raise RuntimeError('server died:\n' + proc.stdout.read().decode())
    return proc


def main():
    _rm_state()
    default_proc = start_server(PORT, 'default')
    setup_proc = start_server(PORT2, 'hermes-setup')

    try:
        default = Client(PORT)
        setup_cl = Client(PORT2)

        # ── boot REST ──
        assert rest(PORT, '/api/status')['ok'] is True
        assert rest(PORT, '/api/sessions')['sessions'] == []
        print('REST boot OK')

        # ── profile minting (Setup bot) ──
        created = setup_cl.rpc('profiles.create', {
            'name': 'hermes-setup', 'description': 'guide', 'share_auth': True, 'soul': '# Setup\n',
        })
        assert created['name'] == 'hermes-setup', created
        try:
            setup_cl.rpc('profiles.create', {'name': 'hermes-setup'})
            raise AssertionError('duplicate profile did not raise')
        except RuntimeError as exc:
            assert 'already exists' in str(exc), exc
        setup_cl.rpc('profiles.configure', {
            'name': 'hermes-setup', 'ui_meta': {'hermes-bots': {'color': '#f2b04c', 'shape': 'blobatar', 'title': 'Setup'}},
        })
        # The DEFAULT process must see the profile (shared state).
        listed = default.rpc('profiles.list')
        names = {p['name'] for p in listed['profiles']}
        assert 'hermes-setup' in names, names
        print('profiles.create/configure/list + cross-process visibility OK')

        # ── Setup's canonical chat: seeded create + adopt-before-mint lookup ──
        seed = [
            {'content': RUNBOOK, 'display_kind': 'hidden', 'role': 'user'},
            {'content': "Hey, welcome — I'm Setup, your Hermes guide.", 'role': 'assistant'},
        ]
        created = setup_cl.rpc('session.create', {
            'hidden': True, 'title': 'Bot Chat', 'model': 'deepseek/deepseek-v4-flash-0731',
            'messages': seed, 'cols': 96, 'source': 'desktop',
        })
        sid = created['session_id']
        assert created['stored_session_id'] == sid
        assert created['hidden'] is True

        found = setup_cl.rpc('session.list', {'include_hidden': True, 'title': 'Bot Chat'})
        assert found['total'] == 1 and found['sessions'][0]['id'] == sid, found
        # Visible-only list hides it (canonical bot chat).
        assert setup_cl.rpc('session.list', {})['total'] == 0
        # A second canonical create ADOPTS instead of minting a duplicate.
        again = setup_cl.rpc('session.create', {'hidden': True, 'title': 'Bot Chat'})
        assert again['session_id'] == sid and again.get('adopted') is True, again
        print('seeded hidden canonical create + title lookup + adopt OK')

        msgs = rest(PORT2, f'/api/sessions/{sid}/messages')
        roles = [m['role'] for m in msgs['messages']]
        hidden_rows = [m for m in msgs['messages'] if m['display_kind'] == 'hidden']
        assert roles[0] == 'user' and roles[1] == 'assistant' and len(hidden_rows) == 1, msgs
        print('seed-message hydration OK')

        # ── the guided flow ──
        reply = setup_cl.submit(sid, 'Sam')
        assert '::onboarding{step="name" value="Sam"}' in reply, reply
        assert '::onboarding{step="look"}' in reply, reply
        print('name turn OK')

        reply = setup_cl.submit(sid, '[setup] accent color: Flame', display_kind='hidden')
        assert '::onboarding{step="connectors"}' in reply, reply
        reply = setup_cl.submit(sid, '[setup] connect later: none for now', display_kind='hidden')
        assert '::onboarding{step="layout"}' in reply, reply
        reply = setup_cl.submit(sid, '[setup] layout: Basic', display_kind='hidden')
        # The fork is quoted from the seeded runbook, not composed here — which
        # is the contract that keeps the mock honest as the real pills change.
        assert FORK_ASK in reply, reply
        print('look/connectors/layout turns + fork ::ask quoted from the runbook OK')

        reply = setup_cl.submit(sid, 'Something else')
        assert FALLBACK_ASK in reply, reply
        print('two-tier fork: "Something else" opens the second ask OK')

        reply = setup_cl.submit(sid, 'Automate something I already do')
        assert 'working on right now' in reply, reply
        # A non-task answer earns the options card. Behavior contract, not a
        # snapshot (FLOW.md:48-51 "generated options … built from that
        # answer"): every chip derives from the answer, fits FirstBuildCard's
        # 60-char cap (directive.tsx:370), and the prose acknowledges it.
        working_answer = 'the SpaceX backlog'
        reply = setup_cl.submit(sid, working_answer)
        assert f'::onboarding{{step="working" value="{working_answer}"}}' in reply, reply
        m = re.search(r'::onboarding\{step="first" options="([^"]*)"\}', reply)
        assert m, reply
        options = m.group(1).split('|')
        assert 2 <= len(options) <= 4, options
        for opt in options:
            assert working_answer in opt, (opt, options)
            assert len(opt) <= 60, (len(opt), opt)
        prose = '\n'.join(l for l in reply.splitlines() if not l.startswith('::onboarding'))
        assert working_answer in prose, reply
        print('fork → what are you working on → answer-derived options card OK')

        reply = setup_cl.submit(sid, options[0])
        assert '::onboarding{step="handoff" task="' in reply, reply
        assert 'surface="bot"' in reply, reply
        assert 'brief="' in reply, reply
        assert 'plan=' not in reply, reply
        print('options tap → handoff directive OK (surface=bot on Basic layout)')

        # ── the machine-setup branch, on a second guide session ──
        # The guide script is gated on canonical identity (hidden 'Bot Chat'
        # on hermes-setup), not profile alone — so fresh guide walks must mint
        # real canonicals. Retire the previous canonical's title first so
        # adopt-before-mint mints fresh instead of resuming it.
        guide = [sid]

        def fresh_guide():
            setup_cl.rpc('session.title', {'session_id': guide[0], 'title': 'Guide (retired)'})
            s = setup_cl.rpc('session.create', {'hidden': True, 'title': 'Bot Chat', 'messages': [
                {'content': RUNBOOK, 'display_kind': 'hidden', 'role': 'user'},
            ]})['session_id']
            assert s != guide[0], 'expected a fresh mint, got an adopt'
            guide[0] = s
            return s

        second = fresh_guide()
        setup_cl.submit(second, 'Sam')
        setup_cl.submit(second, '[setup] accent color: Flame', display_kind='hidden')
        setup_cl.submit(second, '[setup] connect later: none for now', display_kind='hidden')
        setup_cl.submit(second, '[setup] layout: Elite', display_kind='hidden')
        reply = setup_cl.submit(second, 'Help me set up this Mac')
        assert 'mainly want' in reply, reply
        reply = setup_cl.submit(second, 'A bit of everything')
        assert 'plan="machine-setup"' in reply, reply
        # Elite picks the other surface — the layout rule, both ways.
        assert 'surface="session"' in reply, reply
        print('machine branch → handoff with plan=machine-setup, surface=session on Elite OK')

        # ── the working beat's SPECIFIC-task branch + determinism ──
        # onboarding-wizard.ts:495: "SPECIFIC task in mind: skip the options
        # card — go straight to the handoff."
        def working_reply(answer):
            """Walk a fresh guide session to the working beat, answer it,
            and return the reply."""
            s = fresh_guide()
            setup_cl.submit(s, 'Sam')
            setup_cl.submit(s, '[setup] accent color: Flame', display_kind='hidden')
            setup_cl.submit(s, '[setup] connect later: none for now', display_kind='hidden')
            setup_cl.submit(s, '[setup] layout: Basic', display_kind='hidden')
            setup_cl.submit(s, 'Automate something I already do')
            return s, setup_cl.submit(s, answer)

        task_sid, reply = working_reply('Do a deep research on SpaceX')
        assert '::onboarding{step="handoff" task="' in reply, reply
        assert 'step="first"' not in reply, reply  # options card skipped
        m = re.search(r'brief="([^"]*)"', reply)
        assert m and 'SpaceX' in m.group(1), reply
        # The step machine really moved to handoff (shared _handoff path).
        followup = setup_cl.submit(task_sid, 'anything else')
        assert followup and 'handoff card' in followup, followup
        print('task-verb working answer → straight to handoff, brief carries the topic OK')

        _, run_a = working_reply('the SpaceX backlog')
        _, run_b = working_reply('the SpaceX backlog')
        assert run_a == run_b, (run_a, run_b)
        print('working beat is deterministic: identical answer → identical reply OK')

        # ── the roster's identity contract ──
        # Restore Setup's ORIGINAL canonical (the fresh-guide walks retired it)
        # so the roster and the later whisper target the first Bot Chat.
        setup_cl.rpc('session.title', {'session_id': guide[0], 'title': 'Guide (retired)'})
        setup_cl.rpc('session.title', {'session_id': sid, 'title': 'Bot Chat'})
        rows = {p['name']: p for p in default.rpc('profiles.list')['profiles']}
        assert rows['hermes-setup']['canonical_session']['id'] == sid, rows['hermes-setup']
        print('profiles.list reports the canonical Bot Chat per profile OK')

        # ── task bot: mint profile, seeded canonical, visible brief ──
        taskbot_proc = start_server(8901, 'week-tracker')
        try:
            task_cl = Client(8901)
            task_cl.rpc('profiles.create', {'name': 'week-tracker', 'description': 'tracker', 'soul': '# T\n'})
            tseed = [{'content': 'You are a brand-new agent…', 'display_kind': 'hidden', 'role': 'user'}]
            tcreated = task_cl.rpc('session.create', {
                'hidden': True, 'title': 'Bot Chat', 'model': 'deepseek/deepseek-v4-flash-0731',
                'messages': tseed,
            })
            tsid = tcreated['session_id']
            # Cross-process: the Setup server sees the task bot's session.
            seen = setup_cl.rpc('session.list', {'include_hidden': True})
            ids = [s['id'] for s in seen['sessions']]
            assert tsid in ids, ids
            print('task-bot profile + seeded canonical + cross-process session OK')

            reply = task_cl.submit(tsid, 'Build me a weekly tracker.')
            assert '::onboarding{step="progress" title=' in reply, reply
            assert 'permissions' in reply.lower(), reply
            print('task-bot brief → permissions note + progress card OK')

            # ── whisper back into Setup's chat ──
            goodbye = setup_cl.submit(
                sid,
                '[setup] handoff complete — "Weekly tracker" is now building in the Week Tracker bot\'s chat.',
                display_kind='hidden',
            )
            assert goodbye and 'check in' in goodbye, goodbye
            print('[setup] handoff complete → goodbye OK')
        finally:
            taskbot_proc.terminate()
            taskbot_proc.wait(timeout=5)

        # ── profile seams: params['profile'] honored + guide gate is identity ──
        # (i) A create carrying an EXPLICIT profile='default' over the SETUP
        # process's socket lands in 'default' — and its first message gets a
        # generic reply, never the guide's NAME beat (the mock-2 hijack:
        # cross-socket creates used to be stamped with the process profile).
        mis = setup_cl.rpc('session.create', {
            'profile': 'default', 'title': 'Do a deep research on SpaceX',
        })
        msid = mis['session_id']
        row = next(s for s in setup_cl.rpc('session.list', {'include_hidden': True})['sessions']
                   if s['id'] == msid)
        assert row['profile'] == 'default', row
        reply = setup_cl.submit(
            msid, 'Do a deep research on SpaceX — build the first working version and show your work as you go.')
        assert reply is not None
        assert 'step="name"' not in reply and 'Good to meet you' not in reply, reply
        print('explicit profile=default create over the setup socket lands in default, no name beat OK')

        # Adopt-before-mint matches against the PARAM profile's sessions too:
        # a canonical create carrying profile='week-tracker' on the setup
        # socket adopts the task bot's existing canonical.
        adopted = setup_cl.rpc('session.create', {
            'hidden': True, 'title': 'Bot Chat', 'profile': 'week-tracker',
        })
        assert adopted['session_id'] == tsid and adopted.get('adopted') is True, adopted
        print('adopt-before-mint matches against the param profile OK')

        # (ii) A VISIBLE session that really does land on hermes-setup (no
        # profile param → process identity) behaves like a task chat…
        stray = setup_cl.rpc('session.create', {'title': 'Track my week'})
        ssid = stray['session_id']
        row = next(s for s in setup_cl.rpc('session.list', {'include_hidden': True})['sessions']
                   if s['id'] == ssid)
        assert row['profile'] == 'hermes-setup', row
        reply = setup_cl.submit(ssid, 'Track my week — build the first working version.')
        assert '::onboarding{step="progress"' in reply, reply
        assert 'permissions' in reply.lower(), reply
        assert 'step="name"' not in reply and 'Good to meet you' not in reply, reply
        # …while the canonical hidden Bot Chat still runs the guide script
        # (sid sits at step 'after' post-handoff).
        reply = setup_cl.submit(sid, 'are you still there?')
        assert reply and 'Still here' in reply, reply
        print('visible hermes-setup session → task-chat behavior; canonical Bot Chat keeps the guide OK')

        # ── dormant dashboard flow still parses ──
        helper = default.rpc('session.create', {'hidden': True, 'source': 'desktop'})
        hid = helper['session_id']
        mods = default.submit(hid, 'Design starter-screen modules for Sam inside Hermes Desktop. Return 4 modules, at least 3 kinds among them. Reply with ONLY a JSON object: {"modules": [...]}.')
        assert len(json.loads(mods)['modules']) == 4, mods
        blocks_json = json.dumps([
            {'id': 'signal', 'kind': 'feed', 'label': 'The signal', 'prompt': 'p'},
            {'id': 'moves', 'kind': 'action', 'label': 'Three moves', 'prompt': 'p'},
            {'id': 'the-ask', 'kind': 'draft', 'label': 'The ask', 'prompt': 'p'},
        ])
        pop = default.submit(hid, 'Fill in the starter screen… Answer IMMEDIATELY from what you know. Do NOT use any tools. No web search. Reply with ONLY a JSON object: {"blocks": {...}, "extra": [...]}. Blocks: ' + blocks_json)
        parsed = json.loads(pop)
        assert 'moves' in parsed['blocks'] and 'the-ask' in parsed['blocks'], parsed
        print('dormant module-gen + populate JSON OK')

        print('\nALL MOCK CHECKS PASSED')
    finally:
        for proc in (default_proc, setup_proc):
            proc.terminate()
            proc.wait(timeout=5)
        _rm_state()


if __name__ == '__main__':
    main()
