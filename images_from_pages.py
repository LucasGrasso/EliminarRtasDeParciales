from typing import List

from fitz import Document, Matrix
from PIL import Image


def images_from_pages(doc: Document) -> List[Image.Image]:
    """Extract images from pdf file and save them in the output folder.
    Args:
        pdf_path (str): Path to the pdf file.
    Returns:
        list[Image]: List of PIL images.
    """

    res = []
    for page in doc:  # iterate through the pages
        pix = page.get_pixmap(matrix=Matrix(2.0, 2.0))  # render page to an image
        res.append(
            Image.frombuffer(
                "RGB",
                (pix.width, pix.height),
                pix.samples,
                "raw",
                "RGB",
                0,
                1,
            )
        )  # keep image as Python-internal

    return res
