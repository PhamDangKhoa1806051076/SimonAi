"""
Simon Hands – System control & automation tools.
Each function is designed to be called by the Brain via OpenAI Function Calling.
"""

import datetime
import logging
import os
import platform
import subprocess
import webbrowser
from pathlib import Path

import psutil
import pyautogui

LOGGER = logging.getLogger("simon.hands")
pyautogui.FAILSAFE = False


# ------------------------------------------------------------------
# App & Program Control
# ------------------------------------------------------------------

def open_app(app_name: str) -> str:
    """Open an application by name."""
    app_name = app_name.strip()
    system = platform.system()
    try:
        if system == "Windows":
            subprocess.Popen(app_name, shell=True)
        elif system == "Darwin":
            subprocess.Popen(["open", "-a", app_name])
        else:
            subprocess.Popen(app_name, shell=True)
        return f"Đã mở {app_name} thành công."
    except Exception as exc:
        LOGGER.exception("open_app failed: %s", app_name)
        return f"Không mở được {app_name}: {exc}"


def open_website(url: str) -> str:
    """Open a specific URL in the default browser."""
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    try:
        webbrowser.open(url)
        return f"Đã mở trang web: {url}"
    except Exception as exc:
        return f"Không mở được {url}: {exc}"


# ------------------------------------------------------------------
# Web Search
# ------------------------------------------------------------------

def web_search(query: str) -> str:
    """Search the web via Google."""
    webbrowser.open(f"https://www.google.com/search?q={query}")
    return f"Đã tìm kiếm Google: {query}"


# ------------------------------------------------------------------
# System Info
# ------------------------------------------------------------------

def check_cpu() -> str:
    """Get current CPU usage percentage."""
    usage = psutil.cpu_percent(interval=1)
    return f"CPU đang sử dụng {usage}%"


def check_ram() -> str:
    """Get current RAM usage."""
    mem = psutil.virtual_memory()
    used_gb = mem.used / (1024 ** 3)
    total_gb = mem.total / (1024 ** 3)
    avail_mb = mem.available / (1024 ** 2)
    return (
        f"RAM: {mem.percent}% đang sử dụng "
        f"({used_gb:.1f} GB / {total_gb:.1f} GB), "
        f"còn trống {avail_mb:.0f} MB"
    )


def _get_system_disk_path() -> str:
    """Get system disk root path."""
    if platform.system() == "Windows":
        return os.environ.get("SystemDrive", "C:") + "\\"
    return "/"


def check_disk() -> str:
    """Get disk usage for the main drive."""
    drive = _get_system_disk_path()
    disk = psutil.disk_usage(drive)
    used_gb = disk.used / (1024 ** 3)
    total_gb = disk.total / (1024 ** 3)
    free_gb = disk.free / (1024 ** 3)
    drive_label = f" ({drive})" if platform.system() == "Windows" else ""
    return (
        f"Ổ đĩa{drive_label}: {disk.percent}% đã dùng "
        f"({used_gb:.1f} GB / {total_gb:.1f} GB), "
        f"còn trống {free_gb:.1f} GB"
    )


def check_system() -> str:
    """Get comprehensive system information."""
    cpu = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage(_get_system_disk_path())
    boot = datetime.datetime.fromtimestamp(psutil.boot_time())
    uptime = datetime.datetime.now() - boot

    hours, remainder = divmod(int(uptime.total_seconds()), 3600)
    minutes = remainder // 60

    return (
        f"CPU: {cpu}% | "
        f"RAM: {mem.percent}% ({mem.used // (1024**3)}GB/{mem.total // (1024**3)}GB) | "
        f"Disk: {disk.percent}% | "
        f"Uptime: {hours}h {minutes}m | "
        f"OS: {platform.system()} {platform.release()}"
    )


def list_running_processes(limit: int = 15) -> str:
    """List top running processes by memory usage."""
    procs = []
    for proc in psutil.process_iter(["pid", "name", "memory_percent", "cpu_percent"]):
        try:
            info = proc.info
            if info["memory_percent"] and info["memory_percent"] > 0.1:
                procs.append(info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    procs.sort(key=lambda x: x.get("memory_percent", 0), reverse=True)
    procs = procs[:limit]

    if not procs:
        return "Không tìm thấy process nào đáng chú ý."

    lines = []
    for p in procs:
        lines.append(
            f"  {p['name']} (PID {p['pid']}) – "
            f"RAM {p['memory_percent']:.1f}%, CPU {p.get('cpu_percent', 0):.1f}%"
        )
    return "Top processes:\n" + "\n".join(lines)


def kill_process(process_name: str) -> str:
    """Kill a process by name."""
    killed = 0
    for proc in psutil.process_iter(["name"]):
        try:
            if proc.info["name"] and process_name.lower() in proc.info["name"].lower():
                proc.kill()
                killed += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    if killed:
        return f"Đã tắt {killed} process '{process_name}'."
    return f"Không tìm thấy process '{process_name}' đang chạy."


# ------------------------------------------------------------------
# Date & Time
# ------------------------------------------------------------------

def get_datetime() -> str:
    """Get current date and time."""
    now = datetime.datetime.now()
    weekdays_vi = ["Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy", "Chủ Nhật"]
    weekday = weekdays_vi[now.weekday()]
    return f"Hiện tại là {now.strftime('%H:%M:%S')}, {weekday} ngày {now.strftime('%d/%m/%Y')}."


# ------------------------------------------------------------------
# Weather (free, no API key via wttr.in)
# ------------------------------------------------------------------

def get_weather(city: str = "Ho Chi Minh") -> str:
    """Get current weather for a city using wttr.in (free, no API key)."""
    import requests
    try:
        url = f"https://wttr.in/{city}?format=%C+%t+%h+%w&lang=vi"
        resp = requests.get(url, timeout=10, headers={"User-Agent": "curl"})
        if resp.status_code == 200:
            weather = resp.text.strip()
            return f"Thời tiết {city}: {weather}"
        return f"Không lấy được thời tiết cho {city} (HTTP {resp.status_code})"
    except Exception as exc:
        return f"Lỗi khi lấy thời tiết: {exc}"


# ------------------------------------------------------------------
# Screenshot
# ------------------------------------------------------------------

def take_screenshot() -> str:
    """Take a screenshot and save to Desktop."""
    try:
        desktop = Path.home() / "Desktop"
        desktop.mkdir(exist_ok=True)
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = desktop / f"simon_screenshot_{ts}.png"
        screenshot = pyautogui.screenshot()
        screenshot.save(str(filepath))
        return f"Đã chụp màn hình và lưu tại: {filepath}"
    except Exception as exc:
        return f"Không thể chụp màn hình: {exc}"


# ------------------------------------------------------------------
# Keyboard & Mouse
# ------------------------------------------------------------------

def type_text(text: str) -> str:
    """Type text using keyboard automation. Handles Unicode/Vietnamese characters via clipboard."""
    try:
        import pyperclip
        pyperclip.copy(text)
        pyautogui.hotkey("ctrl", "v")
        return f"Đã gõ: {text}"
    except Exception as exc:
        try:
            pyautogui.typewrite(text, interval=0.02)
            return f"Đã gõ: {text}"
        except Exception:
            return f"Lỗi gõ phím: {exc}"


def press_key(key: str) -> str:
    """Press a keyboard key or combination (e.g. 'enter', 'ctrl+c')."""
    try:
        if "+" in key:
            keys = [k.strip() for k in key.split("+")]
            pyautogui.hotkey(*keys)
        else:
            pyautogui.press(key.strip())
        return f"Đã nhấn phím: {key}"
    except Exception as exc:
        return f"Lỗi nhấn phím: {exc}"


# ------------------------------------------------------------------
# System Power
# ------------------------------------------------------------------

def lock_screen() -> str:
    """Lock the computer screen."""
    system = platform.system()
    try:
        if system == "Windows":
            import ctypes
            ctypes.windll.user32.LockWorkStation()
        elif system == "Darwin":
            subprocess.run(["pmset", "displaysleepnow"], check=True)
        else:
            subprocess.run(["loginctl", "lock-session"], check=True)
        return "Đã khóa màn hình."
    except Exception as exc:
        return f"Không thể khóa màn hình: {exc}"


def set_volume(level: int) -> str:
    """Set system volume (0-100). Windows only."""
    if platform.system() != "Windows":
        return "Chức năng này chỉ hỗ trợ Windows."
    try:
        # Use nircmd if available, otherwise PowerShell
        level = max(0, min(100, level))
        # PowerShell approach using AudioDeviceCmdlets or raw COM
        ps_cmd = (
            f"$obj = New-Object -ComObject WScript.Shell; "
            f"1..50 | ForEach-Object {{$obj.SendKeys([char]174)}}; "  # vol down to 0
            f"1..{level // 2} | ForEach-Object {{$obj.SendKeys([char]175)}}"  # vol up
        )
        subprocess.run(["powershell", "-Command", ps_cmd], capture_output=True, timeout=10)
        return f"Đã đặt âm lượng ở mức khoảng {level}%."
    except Exception as exc:
        return f"Không thể điều chỉnh âm lượng: {exc}"


def shutdown_computer(delay: int = 30) -> str:
    """Shutdown the computer with a delay (default 30 seconds)."""
    system = platform.system()
    try:
        if system == "Windows":
            subprocess.Popen(f"shutdown /s /t {delay}", shell=True)
        else:
            subprocess.Popen(f"shutdown -h +{delay // 60}", shell=True)
        return f"Máy tính sẽ tắt sau {delay} giây. Dùng 'shutdown /a' để hủy."
    except Exception as exc:
        return f"Không thể tắt máy: {exc}"


def restart_computer(delay: int = 30) -> str:
    """Restart the computer with a delay (default 30 seconds)."""
    system = platform.system()
    try:
        if system == "Windows":
            subprocess.Popen(f"shutdown /r /t {delay}", shell=True)
        else:
            subprocess.Popen(f"shutdown -r +{delay // 60}", shell=True)
        return f"Máy tính sẽ khởi động lại sau {delay} giây. Dùng 'shutdown /a' để hủy."
    except Exception as exc:
        return f"Không thể khởi động lại máy: {exc}"


def cancel_shutdown() -> str:
    """Cancel a pending shutdown or restart."""
    try:
        if platform.system() == "Windows":
            subprocess.run("shutdown /a", shell=True, capture_output=True)
        else:
            subprocess.run("shutdown -c", shell=True, capture_output=True)
        return "Đã hủy lệnh tắt/khởi động lại máy."
    except Exception as exc:
        return f"Không thể hủy: {exc}"
