from fitz import Document, Rect


def erase_answers(doc: Document, search_strings: set[str]) -> Document:
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
