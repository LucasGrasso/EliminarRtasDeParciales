from io import BytesIO
from typing import Tuple

from fitz import Pixmap
from PIL import Image


def convert_image_to_pixmap(image: Image.Image) -> Tuple[Pixmap, int, int]:
    """Converts a PIL image to a PyMuPDF pixmap.
    Args:
        image (Image): PIL image.
    Returns:
        fitz.Pixmap: PyMuPDF pixmap.
        fitz.Rect: PyMuPDF rectangle.
    """

    img_byte_arr = BytesIO()
    image.save(img_byte_arr, format="JPEG", optimize=True)
    img_byte_arr = img_byte_arr.getvalue()
    pix = Pixmap(img_byte_arr)

    return pix, image.width, image.height
