import pytest
import os
from unittest.mock import patch, mock_open
from app.utils import config  # 确保路径指向你的 config.py

@pytest.fixture(autouse=True)
def reset_config():
    """每个测试开始前重置全局变量，防止干扰"""
    config._config = None
    yield

def test_load_default_config():
    """Happy Path: 测试当文件不存在时，是否加载了默认配置"""
    # 模拟文件不存在的情况
    with patch("os.path.exists", return_value=False):
        loaded = config.load_config()
        assert loaded["neo4j"]["uri"] == "bolt://localhost:7687"
        assert loaded["openai"]["model"] == "gpt-4"

def test_get_neo4j_config_helper():
    """测试辅助获取函数是否能正确拿到子字典"""
    with patch("os.path.exists", return_value=False):
        neo4j_data = config.get_neo4j_config()
        assert "username" in neo4j_data
        assert neo4j_data["username"] == "neo4j"

def test_update_config_and_save():
    """测试更新操作是否触发了保存动作"""
    # 模拟 json.load 出来的初始数据
    initial_data = config.DEFAULT_CONFIG.copy()
    
    # 模拟文件写入
    with patch("os.path.exists", return_value=True), \
         patch("builtins.open", mock_open(read_data='{}')), \
         patch("json.dump") as mock_dump:
        
        success = config.update_openai_config(api_key="sk-test-123", model="gpt-3.5")
        
        assert success is True
        # 验证 json.dump 是否被调用，说明尝试写入硬盘了
        mock_dump.assert_called()
        
        # 验证内存中的 _config 是否已更新
        current_config = config.get_openai_config()
        assert current_config["api_key"] == "sk-test-123"
        assert current_config["model"] == "gpt-3.5"

def test_env_variable_override():
    """Unhappy Path / Edge Case: 测试环境变量是否能成功覆盖默认配置"""
    with patch("os.path.exists", return_value=False), \
         patch.dict(os.environ, {"NEO4J_URI": "bolt://192.168.1.100:7687"}):
        
        loaded = config.load_config()
        assert loaded["neo4j"]["uri"] == "bolt://192.168.1.100:7687"