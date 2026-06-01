import pytest
from alerts.alert_manager import AlertManager

def test_alert_manager_init():
    am = AlertManager("configs/alert_config.yaml")
    assert am.enabled is True
    assert am.gate == 0.55
