from io import BytesIO
from typing import List, Set

import fitz
from sanic import Sanic, exceptions, response

from convert_images_to_pdf import convert_images_to_pdf
from erase_answers import erase_answers as erase_doc_answers
from erase_highlights import erase_highlights
from images_from_pages import images_from_pages

app = Sanic(name="borrar-respuestas-de-Parciales")


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

    search_strings: List[str] = req.form.get("search_strings")

    if not search_strings:
        raise exceptions.NotFound("No search strings were provided")

    set_search_strings: Set[str] = set(search_strings)

    try:
        doc = erase_doc_answers(doc, set_search_strings)
        page_images = images_from_pages(doc=doc)

        for i, image in enumerate(page_images):
            page_images[i] = erase_highlights(image)

        doc = convert_images_to_pdf(image_array=page_images)

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
        raise exceptions.ServerError(f"An error occurred: {e}")


if __name__ == "__main__":
    app.run()
