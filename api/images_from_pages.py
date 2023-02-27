from typing import List

from fitz import Document, Matrix
from PIL.Image import Image, frombuffer

MATRIX = Matrix(1.8, 1.8)


def images_from_pages(doc: Document) -> List[Image]:
    """Extract images from pdf file and save them in the output folder.
    Args:
        pdf_path (str): Path to the pdf file.
    Returns:
        list[Image]: List of PIL images.
    """

    res = []
    for page in doc:  # iterate through the pages
        pix = page.get_pixmap(matrix=MATRIX)  # type: ignore # render page to an image
        res.append(
            frombuffer(
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
