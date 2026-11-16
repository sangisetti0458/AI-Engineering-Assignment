import subprocess
import psutil


def get_cpu_info():
    """
    Collect CPU information using Linux lscpu
    and Python psutil.
    """

    try:
        # Execute a predefined Linux command safely
        result = subprocess.run(
            ["lscpu"],
            capture_output=True,
            text=True,
            timeout=5,
            check=True,
            shell=False
        )

        cpu_data = {}

        # Parse lscpu output
        for line in result.stdout.splitlines():
            if ":" in line:
                key, value = line.split(":", 1)
                cpu_data[key.strip()] = value.strip()

        # Retrieve CPU frequency
        frequency = psutil.cpu_freq()

        max_frequency = (
            frequency.max
            if frequency and frequency.max > 0
            else None
        )

        # Build structured CPU information
        return {
            "status": "success",
            "cpu_model": cpu_data.get("Model name"),
            "architecture": cpu_data.get("Architecture"),
            "physical_cores": psutil.cpu_count(logical=False),
            "logical_processors": psutil.cpu_count(logical=True),
            "max_frequency_mhz": max_frequency
        }

    except FileNotFoundError:
        return {
            "status": "error",
            "message": "lscpu command is not installed."
        }

    except subprocess.TimeoutExpired:
        return {
            "status": "error",
            "message": "CPU inspection timed out."
        }

    except subprocess.CalledProcessError:
        return {
            "status": "error",
            "message": "Unable to retrieve CPU information."
        }

    except Exception as error:
        return {
            "status": "error",
            "message": f"CPU inspection failed: {str(error)}"
        }


if __name__ == "__main__":
    import json

    cpu_info = get_cpu_info()

    print(json.dumps(cpu_info, indent=4))