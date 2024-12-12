"""Common tools."""

import base64
from io import BytesIO
import logging

from PIL import Image
import requests

_LOGGER = logging.getLogger(__name__)

def getIcon(url):
    """Get icon by url."""
    try:
        timeout = 5
        response = requests.get(url, timeout=timeout)
        if response and response.status_code == 200:
            pil_im = Image.open(BytesIO(response.content))
            pil_im = pil_im.convert('RGB')
            b = BytesIO()
            pil_im.save(b, 'jpeg')
            im_bytes = b.getvalue()
            return base64.b64encode(im_bytes).decode()
    except Exception:  # noqa: BLE001
        _LOGGER.error("Failed to get ICON %s: action", url)
