import pytest
from inference.run_image import load_config

def test_config_load():
    config = load_config("configs/inference_config.yaml")
    assert "confidence_threshold" in config
    assert config["confidence_threshold"] == 0.50
