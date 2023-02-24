import io
import os

import fitz
from PIL import Image

ZOOM_X = 2.0  # horizontal zoom
ZOOM_Y = 2.0  # vertical zoom
mat = fitz.Matrix(ZOOM_X, ZOOM_Y)  # zoom factor 2 in each dimension

YELLOW_LOW = (120, 65, 1)
YELLOW_HIGH = (255, 255, 150)
RED_LOW = (200, 0, 0)
RED_HIGH = (255, 0, 0)


def erase_answers(pdf_path: str, search_strings: set[str]) -> fitz.Document:
    """Erase the answers of the true/false choice questions.
    Args:
        pdf_path (str): Path to the pdf file.
        search_strings (set[str]): Set of strings to search for.
    Returns:
        fitz.Document: PyMuPDF document with the answers erased.
    """

    doc: fitz.Document = fitz.open(pdf_path)
    # Loop through the pages of the PDF file
    for _, page in enumerate(doc):
        # Search for the letters you're interested in
        blocks = page.get_text("dict")["blocks"]
        text_blocks = [block for block in blocks if block["type"] == 0]

        boxes: list[fitz.Rect] = []

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


def images_from_pages(doc: fitz.Document) -> list[Image.Image]:
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
            if (
                YELLOW_LOW <= pixel_color <= YELLOW_HIGH
                or RED_LOW <= pixel_color <= RED_HIGH
            ):
                image.putpixel((x, y), (255, 255, 255))  # Set pixel to white

    return image


def convert_image_to_pixmap(image: Image.Image) -> tuple[fitz.Pixmap, fitz.Rect]:
    """Converts a PIL image to a PyMuPDF pixmap.
    Args:
        image (Image): PIL image.
    Returns:
        fitz.Pixmap: PyMuPDF pixmap.
        fitz.Rect: PyMuPDF rectangle.
    """

    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format="PNG")
    img_byte_arr = img_byte_arr.getvalue()
    rect = fitz.Rect(0, 0, image.width, image.height)
    pix = fitz.Pixmap(img_byte_arr)
    return (pix, rect)


def convert_images_to_pdf(image_array: list[Image.Image], pdf_name: str) -> str:
    """Converts a list of PIL images to a pdf file.
    Args:
        image_array (list[Image]): List of PIL images.
        pdf_name (str): Name of the pdf file.
    Returns:
        str: Path to the new pdf file.
    """

    with fitz.open() as doc:
        for image in image_array:
            (pix, rect) = convert_image_to_pixmap(image)
            page = doc.new_page(width=rect.width, height=rect.height)
            page.insert_image(rect, pixmap=pix)
            pix = None

        if not os.path.exists("./OutputSinCorrecciones/"):
            os.makedirs("./OutputSinCorrecciones/")

        output_path: str = f"./OutputSinCorrecciones/{pdf_name}_SinCorreccion.pdf"
        doc.save(output_path)
        return output_path


def main() -> None:
    """Main function."""

    search_strings = set(
        {
            "X",
            "V",
            "F",
            "IF",
            "II",
            "TD",
            "GE",
            "RP",
            "TE",
            "POP",
            "DD",
            "P",
            "RA",
            "RH",
            "B",
            "N",
        }
    )

    for _, file in enumerate(os.listdir("./files")):
        if file.split(".")[1] != "pdf":
            continue
        pdf_path = f"./files/{file}"
        pdf_name = file.split(".")[0]
        doc: fitz.Document = erase_answers(
            pdf_path=pdf_path, search_strings=search_strings
        )

        print("doc", doc)

        page_images = images_from_pages(doc=doc)

        doc.close()

        for i, image in enumerate(page_images):
            page_images[i] = erase_highlights(image)

        file_without_answers_path = convert_images_to_pdf(
            image_array=page_images, pdf_name=pdf_name
        )

        print(f"Nuevo archivo sin respuestas guardado en: {file_without_answers_path}")


if __name__ == "__main__":
    main()
