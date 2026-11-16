
import subprocess
import shutil


def get_gpu_info():
    """Collect GPU information using read-only Linux commands."""

    gpu_info = {
        "status": "success",
        "gpus": [],
        "nvidia_details": None
    }

    try:
        # Check whether lspci is available
        if not shutil.which("lspci"):
            return {
                "status": "error",
                "message": "lspci is not installed."
            }

        # Retrieve PCI device information
        result = subprocess.run(
            ["lspci", "-nn"],
            capture_output=True,
            text=True,
            timeout=5,
            check=True,
            shell=False
        )

        # Identify graphics-related devices
        for line in result.stdout.splitlines():
            lower_line = line.lower()

            if any(keyword in lower_line for keyword in [
                "vga compatible controller",
                "3d controller",
                "display controller"
            ]):
                gpu_info["gpus"].append(line.strip())

        # Check for NVIDIA GPU utility
        if shutil.which("nvidia-smi"):

            nvidia_result = subprocess.run(
                [
                    "nvidia-smi",
                    "--query-gpu=name,memory.total,driver_version",
                    "--format=csv,noheader"
                ],
                capture_output=True,
                text=True,
                timeout=5,
                check=True,
                shell=False
            )

            gpu_info["nvidia_details"] = (
                nvidia_result.stdout.strip()
            )

        return gpu_info

    except subprocess.TimeoutExpired:
        return {
            "status": "error",
            "message": "GPU inspection timed out."
        }

    except subprocess.CalledProcessError:
        return {
            "status": "error",
            "message": "Unable to retrieve GPU information."
        }

    except Exception as error:
        return {
            "status": "error",
            "message": f"GPU inspection failed: {str(error)}"
        }


if __name__ == "__main__":
    import json

    print(
        json.dumps(get_gpu_info(), indent=4)
    )
