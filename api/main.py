from io import BytesIO
from typing import List, Set, Tuple

import fitz
from PIL import Image
from sanic import Sanic, exceptions, html, response
from sanic_cors import CORS

app = Sanic(name="borrar-respuestas-de-Parciales")
cors = CORS(
    app,
    resources={
        "/": {"origins": "*"},
        "/eraseAnswers": {
            "origins": [
                "https://borraryestudiar.lucasgrasso.com.ar",
                "https://api.eliminarrtas.lucasgrasso.com.ar",
            ]
        },
    },
)

### FUNCS ###


def img_dims_to_rect(image_width: int, image_height: int) -> fitz.Rect:
    """Converts image dimensions to a PyMuPDF rectangle.
    Args:
        image_width (int): Image width.
        image_height (int): Image height.
    Returns:
        fitz.Rect: PyMuPDF rectangle.
    """
    return fitz.Rect(0, 0, image_width, image_height)


def convert_image_to_pixmap(image: Image.Image) -> Tuple[fitz.Pixmap, int, int]:
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
    pix = fitz.Pixmap(img_byte_arr)

    return pix, image.width, image.height


async def convert_images_to_pdf(image_array: List[Image.Image]) -> fitz.Document:
    """Converts a list of PIL images to a pdf file.
    Args:
        image_array (list[Image]): List of PIL images.
        pdf_name (str): Name of the pdf file.
    Returns:
        str: Path to the new pdf file.
    """

    _doc = fitz.Document()
    for image in image_array:
        (pix, img_width, img_height) = convert_image_to_pixmap(image)
        rect = img_dims_to_rect(img_width, img_height)
        page: Page = _doc.new_page(width=rect.width, height=rect.height)  # type: ignore
        page.insert_image(rect, pixmap=pix)  # type: ignore
        pix = None

    return _doc


def get_sub_bytestrings_between(string: bytes, start: bytes, end: bytes) -> List[bytes]:
    """Get all the substrings between two strings.
    Args:
    string (bytes): Byte to search in.
    start  (bytes): Byte to start searching.
    end  (bytes): Byte to end searching.
    Returns:
        List[bytes]: List of substrings(bytes) between start and end.
    """

    substrings: List[bytes] = list()
    string_len: int = len(string)

    start_index = 0

    while start_index < string_len:
        start_index = string.find(start, start_index)
        if start_index == -1:
            break
        start_index += len(start)
        end_index = string.find(end, start_index)
        if end_index == -1:
            break
        substrings.append(string[start_index:end_index])
        start_index = end_index + len(end)

    return substrings


def get_substrings_between(string: str, start: str, end: str) -> List[str]:
    """Get all the substrings between two strings.
    Args:
        string (str): String to search in.
        start (str): String to start searching.
        end (str): String to end searching.
    Returns:
        List[str]: List of substrings between start and end.
    """

    substrings: List[str] = list()
    string_len: int = len(string)

    start_index = 0

    while start_index < string_len:
        start_index = string.find(start, start_index)
        if start_index == -1:
            break
        start_index += len(start)
        end_index = string.find(end, start_index)
        if end_index == -1:
            break
        substrings.append(string[start_index:end_index])
        start_index = end_index + len(end)

    return substrings


def decode_TJ_text(text: str) -> str:
    """Decode the text in TJ operator.
    Args:
        text (str): Text to decode.
    Returns:
        str: Decoded text.
    """

    substrings: list[str] = get_substrings_between(
        text,
        "(",
        ")",
    )
    # check if any substring if of type (\nnn ex:\xf1) and decode it(encoding is oct(ord(c)))
    for i, substring in enumerate(substrings):
        if substring.startswith("\\") and len(substring) == 4:
            substrings[i] = chr(int("0o" + substring[1:], 8))
        elif substring.startswith("\\"):
            substrings[i] = substring.replace("\\", "")

    return "".join(substrings)


async def erase_doc_answers(
    _doc: fitz.Document, search_strings: Set[str]
) -> fitz.Document:
    """Erase the answers of the true/false choice questions.
    Args:
        doc (fitz.Document): PyMuPDF document.
        search_strings (set[str]): Set of strings to search for.
    Returns:
        fitz.Document: PyMuPDF document with the answers erased.
    """

    max_str_len: int = 0
    for search_string in search_strings:
        if len(search_string) > max_str_len:
            max_str_len = len(search_string)

    # Loop through the pages of the PDF file
    for page in _doc:
        for xref in page.get_contents():
            stream = _doc.xref_stream(xref)
            bytestring_array: List[bytes] = get_sub_bytestrings_between(
                stream, b"BT", b"ET"
            )
            for bytestring in bytestring_array:
                try:
                    decoded_text = decode_TJ_text(
                        b"".join(bytestring.split(b"TJ")).decode("utf-8")
                    )
                    if any(word in decoded_text for word in search_strings):
                        if len(decoded_text) > max_str_len:
                            continue
                        stream = stream.replace(bytestring, b"() 0.0 TJ")
                        _doc.update_stream(xref, stream)
                except UnicodeDecodeError:
                    continue

    return _doc


async def erase_highlights(image: Image.Image) -> Image.Image:
    """Convert yellow pixels to white and saves it in the same path.
    Args:
        image (Image): PIL image.

    Returns:
        Image: PIL image without yellow and red pixels.
    """

    for x in range(image.width):
        for y in range(image.height):
            pixel_color = image.getpixel((x, y))
            if (110, 110, 110) < pixel_color < (255, 255, 255):
                image.putpixel((x, y), (255, 255, 255))  # Set pixel to white

    return image


MATRIX = fitz.Matrix(1.8, 1.8)


def images_from_pages(doc: fitz.Document) -> List[Image.Image]:
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


### FUNCS ###


@app.route("/", methods=["GET"])
async def index(req):
    return html(
        """
        <!DOCTYPE html>
        <html lang="es">

        <head>
            <meta charset="UTF-8" />
            <link rel="icon" type="image/png" href="https://borraryestudiar.lucasgrasso.com.ar/logo.png" />
            <title>Borrar Respuestas de Parciales</title>
            <meta name="description" content="Borrar Respuestas de Parciales" />
            <meta name="author" content="Lucas Grasso Ramos" />
        </head>

        <style>
            html,
            body {
                scroll-behavior: smooth;
                height: 100vh;
                overflow-y: hidden;
            }

            body {
                display: flex;
                justify-content: center;
                align-items: center;
                font-family: Inter, system-ui, Avenir, Helvetica, Arial, sans-serif;
                line-height: 1.5;
                font-weight: 400;

                color-scheme: light dark;
                color: rgba(255, 255, 255, 0.87);
                background-color: #242424;

                font-synthesis: none;
                text-rendering: optimizeLegibility;
                -webkit-font-smoothing: antialiased;
                -moz-osx-font-smoothing: grayscale;
                -webkit-text-size-adjust: 100%;
            }

            h1 {
                font-size: 3.2em;
                line-height: 1.1;
            }

            .container {
                text-align: center;
            }

            @media (prefers-color-scheme: light) {
                body {
                    color: #213547;
                    background-color: #F3F3F3;
                }
            }
        </style>

        <body>
            <div class="container">
                <img src="https://borraryestudiar.lucasgrasso.com.ar/logo.png" alt="Logo" width="200" height="200" />
                <h1>
                    ¡Hola Estudiantes!
                </h1>
            </div>
        </body>

        </html>
        """
    )


@app.route("/eraseAnswers", methods=["POST"])
async def erase_answers(req):
    file_buffer = req.files.get("file")

    if not file_buffer:
        raise exceptions.NotFound("No file was provided")
    if file_buffer.type != "application/pdf":
        raise exceptions.BadRequest("The file is not a PDF")

    filename = file_buffer.name.split(".")[0].replace(" ", "_")
    file_buffer = BytesIO(file_buffer.body)
    file_buffer.seek(0)
    doc = fitz.Document(stream=file_buffer, filetype="pdf")

    search_strings: List[str] = req.form.getlist("search_strings")

    if not search_strings:
        raise exceptions.NotFound("No search strings were provided")

    set_search_strings: Set[str] = set(search_strings)

    try:
        doc = await erase_doc_answers(doc, set_search_strings)
        page_images = images_from_pages(doc=doc)

        for i, image in enumerate(page_images):
            page_images[i] = await erase_highlights(image)

        doc = await convert_images_to_pdf(image_array=page_images)

        # Return the PDF file as a buffer, then as a response
        buffer = BytesIO()
        doc.save(buffer, garbage=3, deflate=True, clean=True, deflate_images=True)
        doc.close()
        buffer.seek(0)
        return response.raw(
            buffer.getvalue(),
            headers={
                "Content-Type": "application/pdf",
                "Content-Disposition": "attachment",
                "filename": f"{filename}_SinCorrecciones.pdf",
            },
        )

    except Exception as e:
        doc.close()
        raise exceptions.ServerError(message=str(e))


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000)
