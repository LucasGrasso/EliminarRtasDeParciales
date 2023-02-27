from fitz import Rect


def img_dims_to_rect(image_width: int, image_height: int) -> Rect:
    """Converts image dimensions to a PyMuPDF rectangle.
    Args:
        image_width (int): Image width.
        image_height (int): Image height.
    Returns:
        fitz.Rect: PyMuPDF rectangle.
    """
    return Rect(0, 0, image_width, image_height)
