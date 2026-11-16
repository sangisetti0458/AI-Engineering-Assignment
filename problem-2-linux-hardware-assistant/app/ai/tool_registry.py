
from app.tools.cpu import get_cpu_info
from app.tools.memory import get_memory_info
from app.tools.storage import get_storage_info
from app.tools.gpu import get_gpu_info
from app.tools.environment import get_environment_info


# Only approved, read-only inspection tools.
TOOL_REGISTRY = {
    "get_cpu_info": get_cpu_info,
    "get_memory_info": get_memory_info,
    "get_storage_info": get_storage_info,
    "get_gpu_info": get_gpu_info,
    "get_environment_info": get_environment_info
}


def execute_tool(tool_name: str):

    tool = TOOL_REGISTRY.get(tool_name)

    if tool is None:
        return {
            "status": "error",
            "message": f"Tool '{tool_name}' is not allowed."
        }

    try:
        return tool()

    except Exception:
        return {
            "status": "error",
            "message": "Tool execution failed."
        }


if __name__ == "__main__":

    import json

    for tool_name in TOOL_REGISTRY:
        print(f"\nTesting: {tool_name}")
        result = execute_tool(tool_name)
        print(json.dumps(result, indent=4))

    print("\nTesting prohibited tool:")
    print(json.dumps(execute_tool("delete_files"), indent=4))
