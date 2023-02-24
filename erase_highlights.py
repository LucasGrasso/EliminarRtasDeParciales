from PIL import Image

YELLOW_LOW = (120, 65, 1)
YELLOW_HIGH = (255, 255, 150)
RED_LOW = (200, 0, 0)
RED_HIGH = (255, 0, 0)


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
