
from app.tools.cpu import get_cpu_info
from app.tools.memory import get_memory_info
from app.tools.storage import get_storage_info
from app.tools.gpu import get_gpu_info
from app.tools.environment import get_environment_info


def get_all_hardware_info():

    environment = get_environment_info()

    return {
        "environment": environment,
        "hardware": {
            "cpu": get_cpu_info(),
            "memory": get_memory_info(),
            "storage": get_storage_info(),
            "gpu": get_gpu_info()
        }
    }


if __name__ == "__main__":

    import json

    result = get_all_hardware_info()

    print(json.dumps(result, indent=4))
