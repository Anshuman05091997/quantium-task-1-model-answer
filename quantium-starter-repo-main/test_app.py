"""
Test suite for the Pink Morsels Sales Dashboard Dash app.
Uses the standard Dash testing framework (dash.testing) with dash_duo fixture.
"""
import pytest
from app import app


def test_header_is_present(dash_duo):
    """Verify the header is present on the page."""
    dash_duo.start_server(app)
    dash_duo.wait_for_element("h1", timeout=4)
    header = dash_duo.find_element("h1")
    assert "Pink Morsels" in header.text, "Header should contain 'Pink Morsels'"


def test_visualisation_is_present(dash_duo):
    """Verify the sales chart visualisation is present."""
    dash_duo.start_server(app)
    # Wait for the chart to render (callback populates it; Plotly adds svg)
    dash_duo.wait_for_element("#sales-chart", timeout=4)
    dash_duo.wait_for_element("#sales-chart svg", timeout=10)
    chart = dash_duo.find_element("#sales-chart")
    assert chart is not None, "Sales chart visualisation should be present"


def test_region_picker_is_present(dash_duo):
    """Verify the region picker (RadioItems) is present."""
    dash_duo.start_server(app)
    dash_duo.wait_for_element("#region-filter", timeout=4)
    # Region filter uses RadioItems - check for the container and radio inputs
    region_picker = dash_duo.find_element("#region-filter")
    radio_inputs = dash_duo.find_elements("#region-filter input[type='radio']")
    assert region_picker is not None, "Region picker container should be present"
    assert len(radio_inputs) >= 1, "Region picker should have radio options"
