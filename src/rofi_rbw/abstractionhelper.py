import os
import shutil


def is_installed(executable: str) -> bool:
    return shutil.which(executable) is not None


def is_wayland() -> bool:
    return os.environ.get("WAYLAND_DISPLAY", False) is not None

def extract_domain_from_url(url: str) -> str:
    """Extract domain from URL, removing protocol, www, and path/query parameters."""
    import re
    
    # Remove protocol
    url = re.sub(r'^https?://', '', url)
    
    # Remove www prefix
    url = re.sub(r'^www\.', '', url)
    
    # Extract domain (everything before first slash or query parameter)
    domain = url.split('/')[0].split('?')[0].split('#')[0]
    
    return domain
