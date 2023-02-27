from typing import List

from fitz import Document, Page
from PIL import Image

from convert_image_dimentions_to_rect import img_dims_to_rect
from convert_image_to_pixmap import convert_image_to_pixmap


async def convert_images_to_pdf(image_array: List[Image.Image]) -> Document:
    """Converts a list of PIL images to a pdf file.
    Args:
        image_array (list[Image]): List of PIL images.
        pdf_name (str): Name of the pdf file.
    Returns:
        str: Path to the new pdf file.
    """

    _doc = Document()
    for image in image_array:
        (pix, img_width, img_height) = convert_image_to_pixmap(image)
        rect = img_dims_to_rect(img_width, img_height)
        page: Page = _doc.new_page(width=rect.width, height=rect.height)  # type: ignore
        page.insert_image(rect, pixmap=pix)  # type: ignore
        pix = None

    return _doc
