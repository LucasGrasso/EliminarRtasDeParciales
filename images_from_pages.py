from fitz import Document, Matrix
from PIL import Image

ZOOM_X = 2.0  # horizontal zoom
ZOOM_Y = 2.0  # vertical zoom
mat = Matrix(ZOOM_X, ZOOM_Y)  # zoom factor 2 in each dimension


def images_from_pages(doc: Document) -> list[Image.Image]:
    """Extract images from pdf file and save them in the output folder.
    Args:
        pdf_path (str): Path to the pdf file.
    Returns:
        list[Image]: List of PIL images.
    """

    res = []
    for page in doc:  # iterate through the pages
        pix = page.get_pixmap(matrix=mat)  # render page to an image
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
