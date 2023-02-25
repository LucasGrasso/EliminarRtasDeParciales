import json
from io import BytesIO
from typing import List

import fitz
from fastapi import FastAPI, File, Form, Response, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from convert_images_to_pdf import convert_images_to_pdf
from erase import erase_answers as erase_doc_answers
from erase import erase_highlights
from images_from_pages import images_from_pages

app: FastAPI = FastAPI()

origins = [
    "http://borrar.lucasgrasso.com.ar",
    "https://borraryestudi.ar",
    "https://api.eliminarrtas.lucasgrasso.com.ar/",
    "https://eliminarrtasdeparciales.onrender.com/",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/", response_class=HTMLResponse)
def root():
    """Returns the HTML page for the root path."""
    return """
    <html>
        <head>
            <title>Eliminar Respuestas de Parciales</title>
        </head>
        <body>
            <h1>Hola Estudiantes!</h1>
            <span> Subí tu parcial y te devuelvo el mismo parcial pero sin las respuestas.</span>
            <span>Para usarlo, tenés que subir un archivo PDF y escribir las respuestas que querés borrar.</span>
            <span>Por ejemplo, si querés borrar las respuestas que sean X, V o F, tenés que escribir "X,V,F" (sin las comillas).</span>
            <span>El codigo borra automaticamente el subrayado amarillo.</span>
            <h1>¡Suerte rindiendo!</h1>
        </body>
    </html>
    """


@app.post("/eraseAnswers")
async def erase_answers(
    file: UploadFile = File(...), search_strings: List[str] = Form(...)
):
    """Erase answers from a PDF file.

    Args:
        file (UploadFile, optional): The PDF file. Defaults to File(...).
        search_strings (list[str], optional): The search strings. Must be an array of type['"a","b","c"'] Defaults to Form(...).

    Returns:
        Response: The PDF file with the answers erased.
    """

    if not file:
        return {"error": "No file provided"}
    if not search_strings:
        return {"error": "No search strings provided"}

    search_strings_set: set[str] = set()
    try:
        search_strings_set = set(json.loads(search_strings[0]))
    except json.decoder.JSONDecodeError as exception:
        return {"error": f"Error while reading the search strings: {exception}"}

    # Create a PyMuPDF document object from the byte buffer
    try:
        filename: str | None = file.filename
        if not filename:
            return {"error": "File has no filename"}
        if not filename.endswith(".pdf"):
            return {"error": "File is not a PDF"}
        filename = filename.split(".")[0].replace(" ", "_")
        pdf_bytes = await file.read()
        pdf_stream = BytesIO(pdf_bytes)
        doc: fitz.Document = fitz.Document(stream=pdf_stream, filetype="pdf")

        if not doc:
            return {"error": "Error while reading the file"}

        doc = erase_doc_answers(doc, search_strings_set)

        page_images = images_from_pages(doc=doc)

        for i, image in enumerate(page_images):
            page_images[i] = erase_highlights(image)

        doc = convert_images_to_pdf(image_array=page_images)

        buffer = BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        headers = {"Content-Disposition": f'inline; filename="{filename}.pdf"'}

        return Response(
            buffer.getvalue(), headers=headers, media_type="application/pdf"
        )

    except Exception as exception:
        return {"error": f"Error while reading the file: {exception}"}
