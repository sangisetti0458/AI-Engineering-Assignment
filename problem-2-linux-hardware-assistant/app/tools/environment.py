
import os
import platform


def get_environment_info():
    """
    Detect whether the application is running on Linux,
    Windows, WSL1 or WSL2.
    """

    system = platform.system()

    release = platform.release().lower()

    is_wsl = (
        "microsoft" in release
        or "wsl" in os.environ.get("WSL_DISTRO_NAME", "").lower()
    )

    distro = "Unknown"

    try:
        os_info = platform.freedesktop_os_release()
        distro = os_info.get("PRETTY_NAME", "Unknown")
    except (OSError, AttributeError):
        pass

    if system == "Linux" and is_wsl:

        if "microsoft-standard" in release:
            environment_type = "WSL2"
        else:
            environment_type = "WSL (version not confirmed)"

        hardware_scope = "Virtualized Linux environment"

    elif system == "Linux":

        environment_type = "Native Linux"
        hardware_scope = "Linux host environment"

    elif system == "Windows":

        environment_type = "Windows"
        hardware_scope = "Physical or virtual Windows environment"

    else:

        environment_type = system
        hardware_scope = "Unknown"

    return {
        "operating_system": system,
        "distribution": distro,
        "kernel": platform.release(),
        "environment_type": environment_type,
        "is_wsl": is_wsl,
        "hardware_scope": hardware_scope
    }


if __name__ == "__main__":

    import json

    result = get_environment_info()

    print(json.dumps(result, indent=4))
