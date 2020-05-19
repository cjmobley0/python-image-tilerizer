import os
from pathlib import Path
from PIL import Image


def tile_image(img_path: str, zoom_level: int, tile_size: int = 256):
    # Get Image
    image = Image.open(fp=img_path)  # type: Image.Image

    # Create all tiers of zoom level
    for zoom in reversed(range(zoom_level + 1)):
        full_tile_image = scale_image_to_tile(image=image, zoom=zoom)

        # Cut image into pieces
        tilerizer(image=full_tile_image, zoom=zoom, tile_size=tile_size)


def tilerizer(image: Image.Image, zoom: int, tile_size: int = 256):
    """ Break image into equal-sized tiles. Default to 256px """
    width, height = image.width, image.height

    # Check to see that image can be split into even parts
    can_tile = True if ((2 ** zoom) * tile_size) == width and ((2 ** zoom) * tile_size) == height else False
    if can_tile is False and zoom != 0:
        raise AssertionError(f"Zoom level and image height/width mismatching...\n "
                             f"TODO: Add ability to just use scale_image_to_tile method")

    # Gather each tile's origin point - relative (0, 0) point
    origin_points = []
    for col in range(2 ** zoom):
        for row in range(2 ** zoom):
            # Crop for each section
            origin_points.append((col, row))

    # Crop Images based on origin points
    save_to_path = f"{os.getcwd()}/map/{zoom}"

    # Traverse through (Top,Left) points throughout the grid
    for col, row in origin_points:

        # Create column folder if doesn't exist
        col_dir = os.path.join(save_to_path, f"{col}")
        Path(col_dir).mkdir(parents=True, exist_ok=True)

        start_pos = (col * tile_size, row * tile_size)  # Left & Top
        end_pos = ((col + 1) * tile_size, (row + 1) * tile_size)  # Right and Bottom

        cropped_image = image.crop(box=(start_pos + end_pos))
        cropped_image.save(os.path.join(col_dir, f"{row}.png"))


def scale_image_to_tile(image: Image.Image, zoom: int) -> Image.Image:
    """
        Scales image for desired zoom level

        Image scaling is based on smallest tile size (256) multiply by the exponent of the zoom level

        :returns tile_copy: A full-sized tile of equal dimension (ie. 256x256, 512x512)
    """
    if zoom < 0:
        print("Zoom level needs to be more than 0")

    dimension = (2 ** zoom) * 256
    print(f"Scaling image to zoom level: {zoom}.\nImage dimensions: {dimension}x{dimension}")

    # Create base transparent background
    trans_background = create_transparent_background(width=dimension, height=dimension)

    # Scale image to dimension
    scaled_image = scale_image(image=image, dimension=dimension)

    # Draw scaled image onto transparent background
    tile_copy = trans_background.copy()
    # Offset to (center, center)
    offset = ((tile_copy.width - scaled_image.width) // 2, (tile_copy.height - scaled_image.height) // 2)
    tile_copy.paste(scaled_image, offset)

    return tile_copy


def scale_image(image: Image.Image, dimension: int) -> Image.Image:
    """ Helper function to scale image based on which side is larger"""
    image.thumbnail((dimension, dimension))
    return image


def create_transparent_background(width, height) -> Image.Image:
    return Image.new(mode='RGBA', size=(width, height), color=None)


imgpath = "\\put\\your\\path\\here"

tile_image(img_path=imgpath, zoom_level=5)
