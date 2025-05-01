from src.tgen import config


def test_config():
    original_config = config.read_config()
    
    config.write_config(auto_run=False)
    assert config.read_config()["auto_run"] is False
    
    config.write_config(auto_run=True)
    assert config.read_config()["auto_run"] is True
    
    config.write_config(auto_run=original_config.get("auto_run", False))
