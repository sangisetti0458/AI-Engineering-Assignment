
from unittest.mock import patch

from app.ai.tool_registry import TOOL_REGISTRY, execute_tool


def test_only_four_approved_tools_exist():
    expected_tools = {
        "get_cpu_info",
        "get_memory_info",
        "get_storage_info",
        "get_gpu_info",
        "get_environment_info"
    }

    assert set(TOOL_REGISTRY.keys()) == expected_tools


def test_cpu_tool_executes_successfully():
    fake_data = {
        "cpu_model": "Test Intel CPU",
        "architecture": "x86_64"
    }

    with patch.dict(TOOL_REGISTRY, {"get_cpu_info": lambda: fake_data}):
        result = execute_tool("get_cpu_info")

    assert result == fake_data


def test_memory_tool_executes_successfully():
    fake_data = {
        "total_ram_gb": 8,
        "available_ram_gb": 4
    }

    with patch.dict(TOOL_REGISTRY, {"get_memory_info": lambda: fake_data}):
        result = execute_tool("get_memory_info")

    assert result == fake_data


def test_storage_tool_executes_successfully():
    fake_data = {
        "block_devices": []
    }

    with patch.dict(TOOL_REGISTRY, {"get_storage_info": lambda: fake_data}):
        result = execute_tool("get_storage_info")

    assert result == fake_data


def test_gpu_tool_executes_successfully():
    fake_data = {
        "gpus": []
    }

    with patch.dict(TOOL_REGISTRY, {"get_gpu_info": lambda: fake_data}):
        result = execute_tool("get_gpu_info")

    assert result == fake_data


def test_unknown_tool_is_blocked():
    result = execute_tool("delete_files")

    assert result["status"] == "error"
    assert "not allowed" in result["message"]


def test_arbitrary_command_is_blocked():
    result = execute_tool("run_shell_command")

    assert result["status"] == "error"
    assert result["message"] == (
        "Tool 'run_shell_command' is not allowed."
    )


def test_tool_failure_is_handled():

    def failing_tool():
        raise RuntimeError("Simulated failure")

    with patch.dict(TOOL_REGISTRY, {"get_cpu_info": failing_tool}):
        result = execute_tool("get_cpu_info")

    assert result["status"] == "error"
    assert result["message"] == "Tool execution failed."


def test_environment_tool_executes_successfully():

    fake_data = {
        "environment_type": "WSL2",
        "is_wsl": True
    }

    with patch.dict(
        TOOL_REGISTRY,
        {"get_environment_info": lambda: fake_data}
    ):
        result = execute_tool("get_environment_info")

    assert result == fake_data
