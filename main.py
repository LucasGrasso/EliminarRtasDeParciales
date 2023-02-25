from io import BytesIO
from typing import List

import fitz
from fastapi import FastAPI, File, Form, HTTPException, Response, UploadFile
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
            <h1>¡Hola Estudiantes!</h1>
            <span> Subí tu parcial y te devuelvo el mismo parcial pero sin las respuestas.</span>
            <span>Para usarlo, tenés que subir un archivo PDF y escribir las respuestas que querés borrar.</span>
            <span>Por ejemplo, si querés borrar las respuestas que sean X, V o F, tenés que escribir "X,V,F" (sin las comillas).</span>
            <span>El codigo borra automaticamente el subrayado amarillo.</span>
            <h1>¡Suerte rindiendo!</h1>
        </body>
    </html>
    """


@app.post(
    "/eraseAnswers",
    responses={
        200: {
            "content": {"application/pdf": {}},
            "description": "Returns the PDF file with the answers erased.",
        },
    },
)
async def erase_answers(
    file: UploadFile = File(...), search_strings: List[str] = Form(...)
):
    """Erase answers from a PDF file.

    Args:
        file (UploadFile): The PDF file.
        search_strings (list[str]): The search strings. Later converted to a set.

    Returns:
        Response: The PDF file with the answers erased.
    """

    search_strings_set: set[str] = set(search_strings)

    # Create a PyMuPDF document object from the byte buffer

    filename: str | None = file.filename
    if not filename:
        raise HTTPException(status_code=404, detail="File has no filename")
    if not filename.endswith(".pdf"):
        raise HTTPException(status_code=415, detail="File is not a PDF")
    filename = filename.split(".")[0].replace(" ", "_")
    # Convert the file to a byte buffer, then to a PyMuPDF document object
    pdf_bytes = await file.read()
    pdf_stream = BytesIO(pdf_bytes)
    doc: fitz.Document = fitz.Document(stream=pdf_stream, filetype="pdf")

    if not doc:
        raise HTTPException(status_code=422, detail="Error while reading the pdf")

    try:
        # Erase the answers
        doc = erase_doc_answers(doc, search_strings_set)

        page_images = images_from_pages(doc=doc)

        for i, image in enumerate(page_images):
            page_images[i] = erase_highlights(image)

        doc = convert_images_to_pdf(image_array=page_images)

        # Return the PDF file as a buffer, then as a response
        buffer = BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        headers = {"Content-Disposition": f'inline; filename="{filename}.pdf"'}

    except Exception as exception:
        raise HTTPException(status_code=500, detail=str(exception)) from exception

    print(f"Converted {filename} correctly")
    return Response(buffer.getvalue(), headers=headers, media_type="application/pdf")
