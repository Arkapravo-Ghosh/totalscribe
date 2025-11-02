"""System information controller."""

import platform
import subprocess
import re
import torch
import psutil
from helpers.audio_converter import check_ffmpeg_availability


async def get_system_info():
    """Get comprehensive system information."""
    try:
        cpu_count = psutil.cpu_count(logical=False)
        cpu_count_logical = psutil.cpu_count(logical=True)
        memory = psutil.virtual_memory()
        total_memory_gb = round(memory.total / (1024**3), 2)

        gpu_name = "Not Available"
        gpu_cores = "N/A"
        gpu_memory = "N/A"

        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            gpu_memory = f"{round(torch.cuda.get_device_properties(0).total_memory / (1024**3), 2)} GB"
            gpu_cores = torch.cuda.get_device_properties(0).multi_processor_count
        elif torch.backends.mps.is_available():
            try:
                gpu_info = subprocess.check_output(
                    ["system_profiler", "SPDisplaysDataType"]
                ).decode()
                chipset_match = re.search(r"Chipset Model:\s*(.+)", gpu_info)
                if chipset_match:
                    gpu_name = chipset_match.group(1).strip()
                else:
                    gpu_name = "Apple Silicon GPU"
                cores_match = re.search(r"Total Number of Cores:\s*(\d+)", gpu_info)
                if cores_match:
                    gpu_cores = int(cores_match.group(1))
                else:
                    gpu_cores = "Integrated"
                gpu_memory = "Shared with System RAM"
            except:
                gpu_name = "Apple Silicon GPU (MPS)"
                gpu_cores = "Integrated"
                gpu_memory = "Shared with System RAM"

        cpu_name = platform.processor() or "Unknown"
        if not cpu_name or cpu_name == "" or cpu_name == "arm":
            try:
                cpu_name = (
                    subprocess.check_output(
                        ["sysctl", "-n", "machdep.cpu.brand_string"]
                    )
                    .decode()
                    .strip()
                )
            except:
                try:
                    cpu_brand = (
                        subprocess.check_output(["sysctl", "-n", "machdep.cpu.brand"])
                        .decode()
                        .strip()
                    )
                    if cpu_brand:
                        cpu_name = f"Apple {cpu_brand}"
                    else:
                        cpu_name = "Apple Silicon"
                except:
                    cpu_name = "Apple Silicon" if cpu_name == "arm" else "Unknown"

        os_name = platform.system()
        if os_name == "Darwin":
            try:
                macos_version = (
                    subprocess.check_output(["sw_vers", "-productVersion"])
                    .decode()
                    .strip()
                )
                os_name = f"macOS {macos_version}"
            except:
                os_name = f"macOS {platform.release()}"
        elif os_name == "Windows":
            os_name = f"Windows {platform.release()}"
        elif os_name == "Linux":
            try:
                import distro

                os_name = f"{distro.name()} {distro.version()}"
            except:
                os_name = f"Linux {platform.release()}"
        else:
            os_name = f"{platform.system()} {platform.release()}"

        # Check FFmpeg availability
        ffmpeg_available = check_ffmpeg_availability()
        ffmpeg_version = "Not Available"
        if ffmpeg_available:
            try:
                result = subprocess.run(
                    ["ffmpeg", "-version"], capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0:
                    first_line = result.stdout.split("\n")[0]
                    if "ffmpeg version" in first_line:
                        ffmpeg_version = first_line.split(" ")[2]
            except:
                ffmpeg_version = "Available (version unknown)"

        from utils.device import get_device

        device = get_device()

        return {
            "hostname": platform.node(),
            "cpu_name": cpu_name,
            "cpu_cores": cpu_count,
            "cpu_threads": cpu_count_logical,
            "gpu_name": gpu_name,
            "gpu_cores": gpu_cores,
            "total_memory": f"{total_memory_gb} GB",
            "gpu_memory": gpu_memory,
            "os": os_name,
            "device": device,
            "ffmpeg_available": ffmpeg_available,
            "ffmpeg_version": ffmpeg_version,
            "supported_formats": {
                "direct": ["wav", "flac", "ogg", "aiff", "au"],
                "via_ffmpeg": (
                    [
                        "mp3",
                        "mp4",
                        "avi",
                        "mov",
                        "mkv",
                        "webm",
                        "m4a",
                        "aac",
                        "wma",
                        "3gp",
                    ]
                    if ffmpeg_available
                    else []
                ),
                "fallback": ["most audio formats via librosa"],
            },
        }
    except Exception as e:
        return {"error": str(e)}
