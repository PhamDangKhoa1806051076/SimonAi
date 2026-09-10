"""
Simon Tools – Registry of all available tools with OpenAI Function Calling schemas.
Each tool is mapped to (callable, openai_tool_schema).
"""

from simon.hands.system_control import (
    cancel_shutdown,
    check_cpu,
    check_disk,
    check_ram,
    check_system,
    get_datetime,
    get_weather,
    kill_process,
    list_running_processes,
    lock_screen,
    open_app,
    open_website,
    press_key,
    restart_computer,
    set_volume,
    shutdown_computer,
    take_screenshot,
    type_text,
    web_search,
)
from simon.memory.chroma_memory import query_memory, save_to_memory
from simon.smart_home.home_assistant import (
    smart_home_list_devices,
    smart_home_set_brightness,
    smart_home_set_temperature,
    smart_home_toggle,
    smart_home_turn_off,
    smart_home_turn_on,
)
from simon.vision.face_detection import (
    capture_webcam_photo,
    check_camera_for_face,
    toggle_face_watcher,
)




def _schema(name: str, description: str, parameters: dict) -> dict:
    """Helper to build an OpenAI tool schema."""
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": parameters,
        },
    }


# ------------------------------------------------------------------
# All tools with their schemas
# ------------------------------------------------------------------

TOOL_REGISTRY: dict[str, tuple] = {
    "open_app": (
        open_app,
        _schema(
            "open_app",
            "Mở một ứng dụng trên máy tính (ví dụ: chrome, notepad, code, spotify, excel)",
            {
                "type": "object",
                "properties": {
                    "app_name": {
                        "type": "string",
                        "description": "Tên ứng dụng cần mở (ví dụ: 'chrome', 'notepad', 'code')",
                    }
                },
                "required": ["app_name"],
            },
        ),
    ),
    "open_website": (
        open_website,
        _schema(
            "open_website",
            "Mở một trang web cụ thể trong trình duyệt",
            {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "URL trang web cần mở (ví dụ: 'youtube.com', 'https://github.com')",
                    }
                },
                "required": ["url"],
            },
        ),
    ),
    "web_search": (
        web_search,
        _schema(
            "web_search",
            "Tìm kiếm thông tin trên Google",
            {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Từ khóa hoặc câu hỏi cần tìm kiếm",
                    }
                },
                "required": ["query"],
            },
        ),
    ),
    "check_cpu": (
        check_cpu,
        _schema(
            "check_cpu",
            "Kiểm tra mức sử dụng CPU hiện tại (%)",
            {"type": "object", "properties": {}},
        ),
    ),
    "check_ram": (
        check_ram,
        _schema(
            "check_ram",
            "Kiểm tra mức sử dụng RAM hiện tại",
            {"type": "object", "properties": {}},
        ),
    ),
    "check_disk": (
        check_disk,
        _schema(
            "check_disk",
            "Kiểm tra dung lượng ổ đĩa",
            {"type": "object", "properties": {}},
        ),
    ),
    "check_system": (
        check_system,
        _schema(
            "check_system",
            "Kiểm tra tổng quan hệ thống: CPU, RAM, Disk, Uptime, OS",
            {"type": "object", "properties": {}},
        ),
    ),
    "list_running_processes": (
        list_running_processes,
        _schema(
            "list_running_processes",
            "Liệt kê các process đang chạy, sắp xếp theo RAM usage",
            {
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Số lượng process tối đa hiển thị (mặc định 15)",
                    }
                },
            },
        ),
    ),
    "kill_process": (
        kill_process,
        _schema(
            "kill_process",
            "Tắt (kill) một process đang chạy theo tên",
            {
                "type": "object",
                "properties": {
                    "process_name": {
                        "type": "string",
                        "description": "Tên process cần tắt (ví dụ: 'chrome', 'notepad')",
                    }
                },
                "required": ["process_name"],
            },
        ),
    ),
    "get_datetime": (
        get_datetime,
        _schema(
            "get_datetime",
            "Lấy ngày giờ hiện tại",
            {"type": "object", "properties": {}},
        ),
    ),
    "get_weather": (
        get_weather,
        _schema(
            "get_weather",
            "Lấy thông tin thời tiết hiện tại của một thành phố",
            {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "Tên thành phố (ví dụ: 'Ho Chi Minh', 'Ha Noi', 'Da Nang', 'Tokyo')",
                    }
                },
                "required": ["city"],
            },
        ),
    ),
    "take_screenshot": (
        take_screenshot,
        _schema(
            "take_screenshot",
            "Chụp ảnh màn hình và lưu vào Desktop",
            {"type": "object", "properties": {}},
        ),
    ),
    "type_text": (
        type_text,
        _schema(
            "type_text",
            "Gõ một đoạn text tự động bằng bàn phím ảo",
            {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Đoạn text cần gõ",
                    }
                },
                "required": ["text"],
            },
        ),
    ),
    "press_key": (
        press_key,
        _schema(
            "press_key",
            "Nhấn một phím hoặc tổ hợp phím (ví dụ: 'enter', 'ctrl+c', 'alt+f4')",
            {
                "type": "object",
                "properties": {
                    "key": {
                        "type": "string",
                        "description": "Phím hoặc tổ hợp phím (ví dụ: 'enter', 'ctrl+s', 'alt+tab')",
                    }
                },
                "required": ["key"],
            },
        ),
    ),
    "lock_screen": (
        lock_screen,
        _schema(
            "lock_screen",
            "Khóa màn hình máy tính",
            {"type": "object", "properties": {}},
        ),
    ),
    "set_volume": (
        set_volume,
        _schema(
            "set_volume",
            "Đặt mức âm lượng hệ thống (0-100)",
            {
                "type": "object",
                "properties": {
                    "level": {
                        "type": "integer",
                        "description": "Mức âm lượng (0 = tắt tiếng, 100 = tối đa)",
                    }
                },
                "required": ["level"],
            },
        ),
    ),
    "shutdown_computer": (
        shutdown_computer,
        _schema(
            "shutdown_computer",
            "Tắt máy tính (có thời gian chờ mặc định 30 giây)",
            {
                "type": "object",
                "properties": {
                    "delay": {
                        "type": "integer",
                        "description": "Số giây chờ trước khi tắt (mặc định 30)",
                    }
                },
            },
        ),
    ),
    "restart_computer": (
        restart_computer,
        _schema(
            "restart_computer",
            "Khởi động lại máy tính (có thời gian chờ mặc định 30 giây)",
            {
                "type": "object",
                "properties": {
                    "delay": {
                        "type": "integer",
                        "description": "Số giây chờ trước khi khởi động lại (mặc định 30)",
                    }
                },
            },
        ),
    ),
    "cancel_shutdown": (
        cancel_shutdown,
        _schema(
            "cancel_shutdown",
            "Hủy lệnh tắt máy hoặc khởi động lại đã lên lịch",
            {"type": "object", "properties": {}},
        ),
    ),
    "save_memory": (
        save_to_memory,
        _schema(
            "save_memory",
            "Lưu lại thông tin quan trọng, sở thích cá nhân, ghi nhớ hoặc nhắc nhở vào bộ nhớ dài hạn",
            {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Nội dung cần ghi nhớ vào bộ nhớ dài hạn",
                    }
                },
                "required": ["text"],
            },
        ),
    ),
    "search_memory": (
        query_memory,
        _schema(
            "search_memory",
            "Tìm kiếm thông tin đã lưu trong bộ nhớ dài hạn (thói quen, ghi chú, dữ kiện người dùng)",
            {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Nội dung hoặc từ khóa cần tìm trong bộ nhớ",
                    }
                },
                "required": ["query"],
            },
        ),
    ),
    "smart_home_turn_on": (
        smart_home_turn_on,
        _schema(
            "smart_home_turn_on",
            "Bật thiết bị nhà thông minh (đèn, công tắc, quạt, v.v.)",
            {
                "type": "object",
                "properties": {
                    "entity_id": {
                        "type": "string",
                        "description": "ID thiết bị (ví dụ: 'light.living_room', 'switch.fan')",
                    }
                },
                "required": ["entity_id"],
            },
        ),
    ),
    "smart_home_turn_off": (
        smart_home_turn_off,
        _schema(
            "smart_home_turn_off",
            "Tắt thiết bị nhà thông minh (đèn, công tắc, quạt, v.v.)",
            {
                "type": "object",
                "properties": {
                    "entity_id": {
                        "type": "string",
                        "description": "ID thiết bị (ví dụ: 'light.living_room', 'switch.fan')",
                    }
                },
                "required": ["entity_id"],
            },
        ),
    ),
    "smart_home_toggle": (
        smart_home_toggle,
        _schema(
            "smart_home_toggle",
            "Bật/tắt đảo trạng thái thiết bị nhà thông minh",
            {
                "type": "object",
                "properties": {
                    "entity_id": {
                        "type": "string",
                        "description": "ID thiết bị (ví dụ: 'light.living_room')",
                    }
                },
                "required": ["entity_id"],
            },
        ),
    ),
    "smart_home_list_devices": (
        smart_home_list_devices,
        _schema(
            "smart_home_list_devices",
            "Liệt kê danh sách tất cả thiết bị nhà thông minh và trạng thái hiện tại",
            {"type": "object", "properties": {}},
        ),
    ),
    "smart_home_set_brightness": (
        smart_home_set_brightness,
        _schema(
            "smart_home_set_brightness",
            "Điều chỉnh độ sáng đèn thông minh (0-100%)",
            {
                "type": "object",
                "properties": {
                    "entity_id": {
                        "type": "string",
                        "description": "ID đèn (ví dụ: 'light.living_room')",
                    },
                    "brightness_percent": {
                        "type": "integer",
                        "description": "Độ sáng từ 0 đến 100",
                    },
                },
                "required": ["entity_id", "brightness_percent"],
            },
        ),
    ),
    "smart_home_set_temperature": (
        smart_home_set_temperature,
        _schema(
            "smart_home_set_temperature",
            "Điều chỉnh nhiệt độ máy lạnh/điều hòa nhiệt độ",
            {
                "type": "object",
                "properties": {
                    "entity_id": {
                        "type": "string",
                        "description": "ID thiết bị điều hòa (ví dụ: 'climate.ac_bedroom')",
                    },
                    "temperature": {
                        "type": "number",
                        "description": "Nhiệt độ mục tiêu (°C), ví dụ 24.5",
                    },
                },
                "required": ["entity_id", "temperature"],
            },
        ),
    ),
    "check_camera_for_face": (
        check_camera_for_face,
        _schema(
            "check_camera_for_face",
            "Quét qua camera/webcam máy tính để kiểm tra xem có ai hoặc có khuôn mặt nào đang ở trước màn hình không",
            {"type": "object", "properties": {}},
        ),
    ),
    "capture_webcam_photo": (
        capture_webcam_photo,
        _schema(
            "capture_webcam_photo",
            "Chụp một bức ảnh từ webcam máy tính và lưu về Desktop",
            {"type": "object", "properties": {}},
        ),
    ),
    "toggle_face_watcher": (
        toggle_face_watcher,
        _schema(
            "toggle_face_watcher",
            "Bật hoặc tắt chế độ camera quan sát ngầm (tự động phát hiện và chào mừng khi Chủ nhân quay lại máy tính)",
            {
                "type": "object",
                "properties": {
                    "enable": {
                        "type": "boolean",
                        "description": "True để bật quan sát, False để tắt",
                    }
                },
                "required": ["enable"],
            },
        ),
    ),
}




# Flat dict for backward compatibility
TOOLS = {name: func for name, (func, _) in TOOL_REGISTRY.items()}
