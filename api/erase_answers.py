from typing import List, Set, Tuple

from fitz import Document, Rect
from PIL import Image


def rgb2L(colors=Tuple[int, int, int]) -> int:
    R, G, B = colors
    return int(R * 299 / 1000 + G * 587 / 1000 + B * 114 / 1000)


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


def erase_answers(doc: Document, search_strings: Set[str]) -> Document:
    """Erase the answers of the true/false choice questions.
    Args:
        doc (fitz.Document): PyMuPDF document.
        search_strings (set[str]): Set of strings to search for.
    Returns:
        fitz.Document: PyMuPDF document with the answers erased.
    """

    max_str_len: int = len(max(search_strings))

    # Loop through the pages of the PDF file
    for page in doc:
        for xref in page.get_contents():
            stream = doc.xref_stream(xref)
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
                        doc.update_stream(xref, stream)
                except UnicodeDecodeError:
                    continue

    return doc
