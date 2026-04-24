"""Tests for WeatherFlowWebsocketAPI (ws.py)."""

from __future__ import annotations

import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch, PropertyMock

import pytest

from weatherflow4py.models.ws.types import EventType
from weatherflow4py.models.ws.websocket_request import (
    ListenStartMessage,
)
from weatherflow4py.models.ws.websocket_response import (
    ObservationTempestWS,
    RapidWindWS,
)
from weatherflow4py.ws import WeatherFlowWebsocketAPI
from websockets.connection import State as WebSocketState


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

OBS_ST_MESSAGE = json.dumps(
    {
        "type": "obs_st",
        "device_id": 12345,
        "source": "enhanced",
        "serial_number": "ST-00081234",
        "hub_sn": "HB-00061234",
        "firmware_revision": "165",
        "summary": {
            "pressure_trend": "steady",
            "strike_count_1h": 0,
            "strike_count_3h": 0,
            "precip_total_1h": 0.0,
            "strike_last_dist": 0,
            "strike_last_epoch": None,
            "precip_accum_local_yesterday": 0.0,
            "precip_accum_local_yesterday_final": 0,
            "precip_analysis_type_yesterday": 0,
            "feels_like": 20.0,
            "heat_index": 20.0,
            "wind_chill": 20.0,
        },
        "obs": [
            [
                1709057252,
                0.77,
                2.07,
                3.98,
                58,
                3,
                1013.25,
                20.5,
                65,
                10000,
                3.5,
                500,
                0.0,
                0,
                5,
                2,
                2.85,
                1,
                0.0,
                0.0,
                0.0,
                0,
            ]
        ],
    }
)

RAPID_WIND_MESSAGE = json.dumps(
    {
        "type": "rapid_wind",
        "device_id": 12345,
        "ob": [1709057252, 2.5, 180],
        "hub_sn": "HB-00061234",
        "serial_number": "ST-00081234",
    }
)

ACK_MESSAGE = json.dumps({"type": "ack", "id": "test-id-123"})

INVALID_MESSAGE = json.dumps({"type": "unknown_type_xyz"})


def _make_mock_websocket(messages: list[str] | None = None) -> MagicMock:
    """Create a mock websocket that yields messages when iterated."""
    mock_ws = AsyncMock()
    mock_ws.state = WebSocketState.OPEN

    if messages is not None:

        async def _aiter():
            for msg in messages:
                yield msg

        mock_ws.__aiter__ = lambda self: _aiter()

    return mock_ws


# ---------------------------------------------------------------------------
# Basic init / registration tests (synchronous, no connection needed)
# ---------------------------------------------------------------------------


def test_init_defaults():
    """WeatherFlowWebsocketAPI initialises with correct defaults."""
    api = WeatherFlowWebsocketAPI("token123")
    assert api.device_ids == []
    assert "token123" in api.uri
    assert api.websocket is None
    assert api.is_listening is False
    assert api.listen_task is None
    assert api.callbacks == {}


def test_init_with_device_ids():
    api = WeatherFlowWebsocketAPI("token123", device_ids=[111, 222])
    assert api.device_ids == [111, 222]


def test_register_callback():
    api = WeatherFlowWebsocketAPI("t")
    cb = MagicMock()
    api.register_callback(EventType.RAPID_WIND, cb)
    assert api.callbacks[EventType.RAPID_WIND.value] is cb


def test_register_invalid_data_callback():
    api = WeatherFlowWebsocketAPI("t")
    cb = MagicMock()
    api.register_invalid_data_callback(cb)
    assert api.callbacks[EventType.INVALID.value] is cb


def test_register_wind_callback():
    api = WeatherFlowWebsocketAPI("t")
    cb = MagicMock()
    api.register_wind_callback(cb)
    assert api.callbacks[EventType.RAPID_WIND.value] is cb


def test_register_precipitation_callback():
    api = WeatherFlowWebsocketAPI("t")
    cb = MagicMock()
    api.register_precipitation_callback(cb)
    assert api.callbacks[EventType.RAIN.value] is cb


def test_register_lightning_callback():
    api = WeatherFlowWebsocketAPI("t")
    cb = MagicMock()
    api.register_lightning_callback(cb)
    assert api.callbacks[EventType.LIGHTNING_STRIKE.value] is cb


def test_register_observation_callback():
    api = WeatherFlowWebsocketAPI("t")
    cb = MagicMock()
    api.register_observation_callback(cb)
    assert api.callbacks[EventType.OBSERVATION.value] is cb


# ---------------------------------------------------------------------------
# is_connected
# ---------------------------------------------------------------------------


def test_is_connected_no_websocket():
    api = WeatherFlowWebsocketAPI("t")
    assert api.is_connected() is False


def test_is_connected_open():
    api = WeatherFlowWebsocketAPI("t")
    mock_ws = MagicMock()
    mock_ws.state = WebSocketState.OPEN
    api.websocket = mock_ws
    assert api.is_connected() is True


def test_is_connected_closed():
    api = WeatherFlowWebsocketAPI("t")
    mock_ws = MagicMock()
    mock_ws.state = WebSocketState.CLOSED
    api.websocket = mock_ws
    assert api.is_connected() is False


@pytest.mark.asyncio
async def test_close_uses_websocket_state_instead_of_closed_attribute():
    """close() should work with websockets ClientConnection objects that lack `.closed`."""

    class FakeClientConnection:
        def __init__(self) -> None:
            self.state = WebSocketState.OPEN
            self.close_calls = 0

        async def close(self) -> None:
            self.close_calls += 1
            self.state = WebSocketState.CLOSED

    api = WeatherFlowWebsocketAPI("t")
    websocket = FakeClientConnection()
    api.websocket = websocket
    api.is_listening = True

    await api.close()

    assert websocket.close_calls == 1
    assert api.websocket is None
    assert api.is_listening is False


# ---------------------------------------------------------------------------
# last_observation / last_wind / last_observation_time
# ---------------------------------------------------------------------------


def test_last_observation_none_when_no_messages():
    api = WeatherFlowWebsocketAPI("t")
    assert api.last_observation is None


def test_last_wind_none_when_no_messages():
    api = WeatherFlowWebsocketAPI("t")
    assert api.last_wind() is None


def test_last_observation_time_returns_none_when_no_obs():
    api = WeatherFlowWebsocketAPI("t")
    assert api.last_observation_time() is None


def test_last_observation_time_returns_float_when_obs_present():
    api = WeatherFlowWebsocketAPI("t")
    mock_obs = MagicMock()
    mock_obs.epoch = 1_700_000_000  # well in the past
    api.messages["obs_st"] = mock_obs
    result = api.last_observation_time()
    assert isinstance(result, float)
    assert result > 0


# ---------------------------------------------------------------------------
# _send
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_send_calls_websocket_send():
    api = WeatherFlowWebsocketAPI("t")
    mock_ws = AsyncMock()
    api.websocket = mock_ws
    await api._send("hello")
    mock_ws.send.assert_called_once_with("hello")


@pytest.mark.asyncio
async def test_send_does_nothing_when_no_websocket():
    api = WeatherFlowWebsocketAPI("t")
    # Should not raise
    await api._send("hello")


# ---------------------------------------------------------------------------
# listen – sync callback path
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_listen_dispatches_sync_callback():
    """listen() should call a registered sync callback with the parsed response."""
    api = WeatherFlowWebsocketAPI("t")

    received = []

    def obs_cb(msg):
        received.append(msg)

    api.register_observation_callback(obs_cb)

    mock_ws = _make_mock_websocket([OBS_ST_MESSAGE])
    api.websocket = mock_ws

    await api.listen()

    assert len(received) == 1
    assert isinstance(received[0], ObservationTempestWS)


@pytest.mark.asyncio
async def test_listen_dispatches_async_callback():
    """listen() should await an async callback."""
    api = WeatherFlowWebsocketAPI("t")

    received = []

    async def wind_cb(msg):
        received.append(msg)

    api.register_wind_callback(wind_cb)

    mock_ws = _make_mock_websocket([RAPID_WIND_MESSAGE])
    api.websocket = mock_ws

    await api.listen()

    assert len(received) == 1
    assert isinstance(received[0], RapidWindWS)


@pytest.mark.asyncio
async def test_listen_no_callback_for_message_type():
    """listen() should silently handle messages with no registered callback."""
    api = WeatherFlowWebsocketAPI("t")
    mock_ws = _make_mock_websocket([OBS_ST_MESSAGE])
    api.websocket = mock_ws

    # No callback registered – should not raise
    await api.listen()
    assert "obs_st" in api.messages


@pytest.mark.asyncio
async def test_listen_invalid_message_dispatches_invalid_callback():
    """listen() should call the INVALID callback for unrecognised message types."""
    api = WeatherFlowWebsocketAPI("t")

    invalid_received = []

    def invalid_cb(data):
        invalid_received.append(data)

    api.register_invalid_data_callback(invalid_cb)

    mock_ws = _make_mock_websocket([INVALID_MESSAGE])
    api.websocket = mock_ws

    await api.listen()

    assert len(invalid_received) == 1
    assert invalid_received[0]["type"] == "unknown_type_xyz"


@pytest.mark.asyncio
async def test_listen_invalid_message_async_invalid_callback():
    """listen() awaits async INVALID callback."""
    api = WeatherFlowWebsocketAPI("t")

    invalid_received = []

    async def invalid_cb(data):
        invalid_received.append(data)

    api.register_invalid_data_callback(invalid_cb)

    mock_ws = _make_mock_websocket([INVALID_MESSAGE])
    api.websocket = mock_ws

    await api.listen()

    assert len(invalid_received) == 1


@pytest.mark.asyncio
async def test_listen_invalid_message_no_invalid_callback(caplog):
    """listen() logs a warning when there's no INVALID callback."""
    import logging

    api = WeatherFlowWebsocketAPI("t")
    mock_ws = _make_mock_websocket([INVALID_MESSAGE])
    api.websocket = mock_ws

    with caplog.at_level(logging.WARNING):
        await api.listen()

    assert any("Unrecognized" in r.message for r in caplog.records)


@pytest.mark.asyncio
async def test_listen_sets_is_listening_false_on_exit():
    """listen() should reset is_listening to False even on normal exit."""
    api = WeatherFlowWebsocketAPI("t")
    mock_ws = _make_mock_websocket([])  # no messages, exits immediately
    api.websocket = mock_ws

    await api.listen()

    assert api.is_listening is False


# ---------------------------------------------------------------------------
# connect
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_connect_establishes_websocket():
    """connect() should set self.websocket and create a listen task."""
    api = WeatherFlowWebsocketAPI("t")
    # Reset shared websocket so test is isolated
    WeatherFlowWebsocketAPI._shared_websocket = None

    mock_ws = _make_mock_websocket([])

    with patch(
        "weatherflow4py.ws.websockets.connect", new_callable=AsyncMock
    ) as mock_connect:
        mock_connect.return_value = mock_ws

        await api.connect()

        assert api.websocket is mock_ws
        assert api.listen_task is not None
        # Clean up background task
        api.listen_task.cancel()
        try:
            await api.listen_task
        except (asyncio.CancelledError, AssertionError):
            pass

    # Reset for other tests
    WeatherFlowWebsocketAPI._shared_websocket = None


@pytest.mark.asyncio
async def test_connect_reuses_shared_websocket():
    """A second connect() call reuses the class-level _shared_websocket."""
    WeatherFlowWebsocketAPI._shared_websocket = None

    api1 = WeatherFlowWebsocketAPI("t")
    api2 = WeatherFlowWebsocketAPI("t")

    mock_ws = _make_mock_websocket([])

    with patch(
        "weatherflow4py.ws.websockets.connect", new_callable=AsyncMock
    ) as mock_connect:
        mock_connect.return_value = mock_ws

        await api1.connect()
        # Clear listen_task for api1
        if api1.listen_task:
            api1.listen_task.cancel()
            try:
                await api1.listen_task
            except (asyncio.CancelledError, AssertionError):
                pass

        await api2.connect()
        if api2.listen_task:
            api2.listen_task.cancel()
            try:
                await api2.listen_task
            except (asyncio.CancelledError, AssertionError):
                pass

    # connect() should only have been called once (shared websocket)
    mock_connect.assert_called_once()
    assert api1.websocket is api2.websocket

    WeatherFlowWebsocketAPI._shared_websocket = None


# ---------------------------------------------------------------------------
# send_message
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_send_message():
    api = WeatherFlowWebsocketAPI("t")
    mock_ws = AsyncMock()
    api.websocket = mock_ws

    msg = ListenStartMessage(device_id=12345)
    await api.send_message(msg)

    mock_ws.send.assert_called_once()


# ---------------------------------------------------------------------------
# send_message_and_wait
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_send_message_and_wait_timeout():
    """send_message_and_wait returns None on timeout."""
    api = WeatherFlowWebsocketAPI("t")
    mock_ws = AsyncMock()
    api.websocket = mock_ws

    result = await api.send_message_and_wait(
        ListenStartMessage(device_id=1), timeout=0.01
    )
    assert result is None


@pytest.mark.asyncio
async def test_send_message_and_wait_restores_original_callback():
    """send_message_and_wait restores a pre-existing ACK callback after timeout."""
    api = WeatherFlowWebsocketAPI("t")
    mock_ws = AsyncMock()
    api.websocket = mock_ws

    original_cb = MagicMock()
    api.callbacks[EventType.ACKNOWLEDGEMENT.value] = original_cb

    await api.send_message_and_wait(ListenStartMessage(device_id=1), timeout=0.01)

    assert api.callbacks[EventType.ACKNOWLEDGEMENT.value] is original_cb


@pytest.mark.asyncio
async def test_send_message_and_wait_removes_temp_callback_when_none_before():
    """send_message_and_wait removes the temp ACK callback if none existed before."""
    api = WeatherFlowWebsocketAPI("t")
    mock_ws = AsyncMock()
    api.websocket = mock_ws

    assert EventType.ACKNOWLEDGEMENT.value not in api.callbacks

    await api.send_message_and_wait(ListenStartMessage(device_id=1), timeout=0.01)

    assert EventType.ACKNOWLEDGEMENT.value not in api.callbacks


# ---------------------------------------------------------------------------
# stop_all_listeners
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_stop_all_listeners_sends_messages():
    """stop_all_listeners sends stop messages for each device_id."""
    api = WeatherFlowWebsocketAPI("t", device_ids=[111, 222])
    mock_ws = AsyncMock()
    api.websocket = mock_ws

    # send_message_and_wait will timeout (no real ACK), but we just need sends to happen
    await api.stop_all_listeners()

    # 2 devices × 2 stop messages = 4 sends (each times out)
    assert mock_ws.send.call_count == 4


@pytest.mark.asyncio
async def test_stop_all_listeners_no_devices():
    """stop_all_listeners with no device_ids does nothing."""
    api = WeatherFlowWebsocketAPI("t")
    mock_ws = AsyncMock()
    api.websocket = mock_ws

    await api.stop_all_listeners()

    mock_ws.send.assert_not_called()


# ---------------------------------------------------------------------------
# close
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_close_when_not_connected_is_noop():
    """close() returns early if not connected."""
    api = WeatherFlowWebsocketAPI("t")
    # websocket is None → is_connected() is False
    await api.close()  # should not raise


@pytest.mark.asyncio
async def test_close_cancels_listen_task_and_closes_websocket():
    """close() cancels listen task and closes the websocket."""
    api = WeatherFlowWebsocketAPI("t")

    mock_ws = AsyncMock()
    mock_ws.state = WebSocketState.OPEN
    # After close() is called, state transitions to CLOSED
    type(mock_ws).state = PropertyMock(
        side_effect=[
            WebSocketState.OPEN,  # is_connected() check
            WebSocketState.OPEN,  # if self.websocket branch
            WebSocketState.CLOSED,  # final state check in finally
        ]
    )
    api.websocket = mock_ws

    # Create a real (but already-done) task so cancel() path is skipped
    async def _noop():
        pass

    done_task = asyncio.create_task(_noop())
    await done_task  # ensure it's done
    api.listen_task = done_task

    await api.close()

    mock_ws.close.assert_called_once()
    assert api.websocket is None
