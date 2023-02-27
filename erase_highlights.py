from PIL.Image import Image


async def erase_highlights(image: Image) -> Image:
    """Convert yellow pixels to white and saves it in the same path.
    Args:
        image (Image): PIL image.

    Returns:
        Image: PIL image without yellow and red pixels.
    """

    for x in range(image.width):
        for y in range(image.height):
            (r, g, b) = image.getpixel((x, y))
            if r > 150 and g > 150 and b < 150:
                image.putpixel((x, y), (255, 255, 255))  # Set pixel to white

    return image
