"""Required policies buffer candidate assistant text before host approval."""

from types import SimpleNamespace

from run_agent import AIAgent


def _agent(*, buffered: bool):
    delivered = []
    return SimpleNamespace(
        _finalization_buffering_required=buffered,
        _stream_writer_superseded=lambda: False,
        _stream_needs_break=False,
        _stream_think_scrubber=None,
        _stream_context_scrubber=None,
        _strip_think_blocks=lambda text: text,
        _current_streamed_assistant_text="",
        stream_delta_callback=delivered.append,
        _stream_callback=None,
        _record_streamed_assistant_text=lambda text: delivered.append(f"record:{text}"),
        _stream_hook_base_payload=lambda: {},
        delivered=delivered,
    )


def test_required_policy_buffer_suppresses_candidate_deltas():
    agent = _agent(buffered=True)
    AIAgent._fire_stream_delta(agent, "candidate secret")
    assert agent.delivered == []


def test_required_policy_buffers_interim_and_codex_commentary():
    delivered = []
    agent = SimpleNamespace(
        _finalization_buffering_required=True,
        interim_assistant_callback=lambda *args, **kwargs: delivered.append((args, kwargs)),
    )

    AIAgent._fire_streamed_codex_commentary(agent, "candidate commentary")
    AIAgent._emit_interim_assistant_message(
        agent, {"role": "assistant", "content": "candidate interim"}
    )
    AIAgent._fire_reasoning_delta(agent, "candidate reasoning")

    assert delivered == []


def test_required_policy_discards_scrubber_tails_instead_of_flushing_them():
    delivered = []

    class Scrubber:
        def flush(self):
            return "candidate tail"

        def feed(self, value):
            return value

    agent = SimpleNamespace(
        _finalization_buffering_required=True,
        _stream_think_scrubber=Scrubber(),
        _stream_context_scrubber=Scrubber(),
        stream_delta_callback=delivered.append,
        _stream_callback=delivered.append,
        _current_streamed_assistant_text="candidate",
    )
    AIAgent._reset_stream_delivery_tracking(agent)
    assert delivered == []
    assert agent._current_streamed_assistant_text == ""


def test_required_policy_redacts_interim_text_before_tool_turn_persistence():
    agent = SimpleNamespace(_finalization_buffering_required=True)
    message = {
        "role": "assistant",
        "content": "candidate completion",
        "reasoning": "candidate reasoning",
        "codex_message_items": [{"phase": "commentary"}],
        "tool_calls": [{"id": "call-1"}],
    }
    AIAgent._redact_buffered_interim_assistant_message(agent, message)
    assert message == {
        "role": "assistant",
        "content": "",
        "tool_calls": [{"id": "call-1"}],
    }


def test_stream_end_observer_receives_no_candidate(monkeypatch):
    observed = []
    monkeypatch.setattr(
        "agent.plugin_stream_hooks.enqueue_plugin_stream_hook",
        lambda name, **payload: observed.append((name, payload)),
    )
    agent = SimpleNamespace(
        _finalization_buffering_required=True,
        _stream_hook_base_payload=lambda: {"turn_id": "turn"},
    )
    AIAgent._emit_stream_end(
        agent,
        final_text="CANDIDATE SECRET",
        finished=True,
        error=None,
    )
    assert observed[0][1]["final_text"] == ""


def test_unprotected_session_streaming_is_unchanged(monkeypatch):
    monkeypatch.setattr(
        "agent.plugin_stream_hooks.enqueue_plugin_stream_hook", lambda *_a, **_kw: None
    )
    agent = _agent(buffered=False)
    AIAgent._fire_stream_delta(agent, "hello")
    assert agent.delivered == ["hello", "record:hello"]
