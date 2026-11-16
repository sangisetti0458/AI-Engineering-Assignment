import psutil


def get_memory_info():
    """Retrieve system RAM and swap memory information."""

    try:
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()

        return {
            "status": "success",
            "total_ram_gb": round(memory.total / (1024 ** 3), 2),
            "used_ram_gb": round(memory.used / (1024 ** 3), 2),
            "available_ram_gb": round(memory.available / (1024 ** 3), 2),
            "ram_usage_percent": memory.percent,
            "total_swap_gb": round(swap.total / (1024 ** 3), 2),
            "used_swap_gb": round(swap.used / (1024 ** 3), 2)
        }

    except Exception as error:
        return {
            "status": "error",
            "message": f"Memory inspection failed: {str(error)}"
        }


if __name__ == "__main__":
    import json

    print(json.dumps(get_memory_info(), indent=4))