"""Exercise actual Streamlit widgets without network or scripted production replies."""
from unittest.mock import Mock

import pytest
import streamlit as st
from streamlit.testing.v1 import AppTest

from speedlimit.air import AirSource
from speedlimit.config import ROOT, load_config


@pytest.fixture
def gui():
    st.cache_resource.clear()
    app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30).run()
    assert not app.exception
    source = Mock()
    source.fixture.return_value = AirSource(load_config()).fixture("clear")
    model = Mock()
    model.decide.return_value = {"status": "valid", "limit": 80, "reason": "Clear test reading",
                                "model": "test double", "ollama_status": "test_double"}
    app.session_state["source"] = source
    app.session_state["air_model"] = model
    app.selectbox[0].set_value("clear").run()
    return app, source, model


def test_gui_on_demand_and_redraw_no_repeat(gui):
    app, source, model = gui
    app.button[0].click().run()
    assert not app.exception
    assert app.metric[0].value == "80 km/h"
    assert model.decide.call_count == 1
    app.number_input[2].set_value(11.).run()
    assert model.decide.call_count == 1
    assert app.session_state["last_complete"]


def test_gui_start_tick_stop(gui):
    app, source, model = gui
    app.button[1].click().run()
    assert app.session_state["running"] and model.decide.call_count == 1
    app.run()
    assert model.decide.call_count == 1
    app.session_state["next_due"] = 0.
    app.run()
    assert model.decide.call_count == 2
    app.button[2].click().run()
    assert not app.session_state["running"]
    app.session_state["next_due"] = 0.
    app.run()
    assert model.decide.call_count == 2


def test_gui_incomplete_keeps_last_complete(gui):
    app, source, model = gui
    app.button[0].click().run()
    previous = app.session_state["last_complete"]
    model.decide.return_value = {"status": "unavailable", "limit": None,
                                "reason": "Ollama unavailable", "ollama_status": "unavailable"}
    app.button[0].click().run()
    assert not app.exception
    assert not app.metric and app.error
    assert app.session_state["history"][0]["limit"] is None
    assert app.session_state["last_complete"] == previous


def test_gui_busy_guard(gui):
    app, source, model = gui
    app.session_state["busy"] = True
    app.session_state["running"] = True
    app.session_state["next_due"] = 0.
    app.run()
    assert model.decide.call_count == 0
    assert app.button[0].disabled


def test_gui_history_is_bounded(gui):
    app, source, model = gui
    app.button[0].click().run()
    prior = app.session_state["history"][0]
    app.session_state["history"] = [prior] * 20
    app.button[0].click().run()
    assert len(app.session_state["history"]) == 20
    assert app.session_state["history"][0]["snapshot_time"] != prior["snapshot_time"]
    assert not app.exception
