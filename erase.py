from typing import Set

from fitz import Document, Rect
from PIL import Image


def erase_highlights(image: Image.Image) -> Image.Image:
    """Convert yellow pixels to white and saves it in the same path.
    Args:
        image (Image): PIL image.

    Returns:
        Image: PIL image without yellow and red pixels.
    """

    for x in range(image.width):
        for y in range(image.height):
            pixel_color = image.getpixel((x, y))
            if (120, 65, 1) <= pixel_color <= (255, 255, 150) or (
                200,
                0,
                0,
            ) <= pixel_color <= (255, 0, 0):
                image.putpixel((x, y), (255, 255, 255))  # Set pixel to white

    return image


def erase_answers(doc: Document, search_strings: Set[str]) -> Document:
    """Erase the answers of the true/false choice questions.
    Args:
        doc (fitz.Document): PyMuPDF document.
        search_strings (set[str]): Set of strings to search for.
    Returns:
        fitz.Document: PyMuPDF document with the answers erased.
    """

    # Loop through the pages of the PDF file
    for page in doc:
        # Search for the letters you're interested in
        blocks = page.get_text("dict")["blocks"]
        text_blocks = [block for block in blocks if block["type"] == 0]

        boxes: list[Rect] = []

        for block in text_blocks:
            for lines in block["lines"]:
                for words in lines["spans"]:
                    if any(word in words["text"] for word in search_strings):
                        if len(words["text"]) <= 5:
                            boxes.append(words["bbox"])

        if len(boxes) != 0:
            for bbox in boxes:
                page.add_rect_annot(bbox)
                page.draw_rect(bbox, color=(1, 1, 1), fill=(1, 1, 1), width=1)

    return doc
