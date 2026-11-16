import json
import subprocess
import psutil


def get_storage_info():
    """Collect storage device and filesystem information."""

    try:
        # Read-only command to inspect block devices
        result = subprocess.run(
            [
                "lsblk",
                "--json",
                "-o",
                "NAME,SIZE,TYPE,FSTYPE,MOUNTPOINT,MODEL,ROTA,TRAN"
            ],
            capture_output=True,
            text=True,
            timeout=5,
            check=True,
            shell=False
        )

        devices = json.loads(result.stdout)

        # Collect mounted filesystem information
        partitions = []

        for partition in psutil.disk_partitions(all=False):
            try:
                usage = psutil.disk_usage(partition.mountpoint)

                partitions.append({
                    "device": partition.device,
                    "mountpoint": partition.mountpoint,
                    "filesystem": partition.fstype,
                    "total_gb": round(
                        usage.total / (1024 ** 3), 2
                    ),
                    "used_gb": round(
                        usage.used / (1024 ** 3), 2
                    ),
                    "free_gb": round(
                        usage.free / (1024 ** 3), 2
                    ),
                    "usage_percent": usage.percent
                })

            except (PermissionError, OSError):
                continue

        return {
            "status": "success",
            "block_devices": devices.get("blockdevices", []),
            "partitions": partitions
        }

    except FileNotFoundError:
        return {
            "status": "error",
            "message": "lsblk command is not installed."
        }

    except subprocess.TimeoutExpired:
        return {
            "status": "error",
            "message": "Storage inspection timed out."
        }

    except subprocess.CalledProcessError:
        return {
            "status": "error",
            "message": "Unable to retrieve storage devices."
        }

    except (json.JSONDecodeError, ValueError):
        return {
            "status": "error",
            "message": "Invalid storage information returned."
        }

    except Exception as error:
        return {
            "status": "error",
            "message": f"Storage inspection failed: {str(error)}"
        }


if __name__ == "__main__":
    print(json.dumps(get_storage_info(), indent=4))
