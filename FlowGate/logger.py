import time
from enum import Enum

class LogLevel(Enum):
    INFO = "INFO"
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"
    ERROR = "ERROR"
    DEBUG = "DEBUG"

class Colors:
    """ANSI color codes for terminal output"""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    
    # Colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    
    # Bright colors
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"

def get_color_for_event(event: str) -> str:
    """Returns color based on event type"""
    event_lower = event.lower()
    
    if "start" in event_lower or "end" in event_lower:
        return Colors.BRIGHT_MAGENTA
    elif "success" in event_lower or "ok" in event_lower or "connected" in event_lower:
        return Colors.BRIGHT_GREEN
    elif "fail" in event_lower or "error" in event_lower or "timeout" in event_lower:
        return Colors.BRIGHT_RED
    elif "warning" in event_lower or "no_backend" in event_lower:
        return Colors.BRIGHT_YELLOW
    elif "selected" in event_lower or "received" in event_lower:
        return Colors.BRIGHT_CYAN
    elif "closed" in event_lower:
        return Colors.BRIGHT_BLACK
    else:
        return Colors.BRIGHT_BLUE

def log(event, **fields):
    """Enhanced logging with colors and better formatting"""
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    color = get_color_for_event(event)
    
    # Format fields
    if fields:
        formatted_fields = []
        for k, v in fields.items():
            formatted_fields.append(f"{Colors.BRIGHT_WHITE}{k}{Colors.RESET}{color}={Colors.BRIGHT_WHITE}{v}{Colors.RESET}")
        data = " ".join(formatted_fields)
    else:
        data = ""
    
    # Special formatting for request boundaries
    if "START" in event or "END" in event:
        separator = "━" * 60
        print(f"{color}{Colors.BOLD}{separator}{Colors.RESET}")
        print(f"{color}{Colors.BOLD}{event}{Colors.RESET}")
        print(f"{color}{Colors.BOLD}{separator}{Colors.RESET}")

        if "END" in event:
            print("\n")
    else:
        # Regular log format: [timestamp] event field1=value1 field2=value2
        print(f"{Colors.BRIGHT_BLACK}[{ts}]{Colors.RESET} {Colors.BOLD}{color}{event}{Colors.RESET} {data}")