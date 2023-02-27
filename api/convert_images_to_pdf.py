from typing import List

from fitz import Document, Page
from PIL import Image

from convert_image_to_pixmap import convert_image_to_pixmap


def convert_images_to_pdf(image_array: List[Image.Image]) -> Document:
    """Converts a list of PIL images to a pdf file.
    Args:
        image_array (list[Image]): List of PIL images.
        pdf_name (str): Name of the pdf file.
    Returns:
        str: Path to the new pdf file.
    """

    doc = Document()
    for image in image_array:
        (pix, rect) = convert_image_to_pixmap(image)
        page: Page = doc.new_page(width=rect.width, height=rect.height)
        page.insert_image(rect, pixmap=pix)
        pix = None

    return doc
