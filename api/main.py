from io import BytesIO
from typing import List, Set

import fitz
from sanic import Sanic, exceptions, html, response

from convert_images_to_pdf import convert_images_to_pdf
from erase_answers import erase_answers as erase_doc_answers
from erase_highlights import erase_highlights
from images_from_pages import images_from_pages

app = Sanic(name="borrar-respuestas-de-Parciales")


@app.route("/", methods=["GET"])
async def index():
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
