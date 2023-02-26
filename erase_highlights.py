from typing import Tuple

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
            if (125, 125, 0) <= pixel_color <= (255, 255, 0) or (
                200,
                0,
                0,
            ) <= pixel_color <= (255, 0, 0):
                image.putpixel((x, y), (255, 255, 255))  # Set pixel to white

    return image
