import os
from PIL import Image
from pathlib import Path


class Tilerizer:
    def __init__(self,
                 source_image: str,
                 destination: str,
                 zoom_level: int,
                 tile_size: int = 256,
                 background_color: [str, bool] = None):
        """
        Cut an image into 2^(zoom_level) even square pieces

        :param source_image: Path to image desired to tile
        :param destination: Path to save images
        :param zoom_level: The number of tiers of varying dimensions
        :param tile_size: The width/height length of each square
        :param background_color: The desired background color. Transparent by default TODO common color names
        """
        self._src_image = Image.open(fp=source_image)  # type: Image.Image
        self._destination = destination
        self.zoom_level = zoom_level
        self.tile_size = tile_size
        self.background_color = background_color

    @property
    def src_image(self) -> Image.Image:
        """ Return a copy of the original source image """
        return self._src_image.copy()

    @src_image.setter
    def src_image(self, source_image: Image.Image):
        if not self._src_image:
            #TODO Path validation
            self._src_image = source_image
        else:
            print("Source image has previously been set before...")

    @property
    def destination(self):
        """ Folder path of where images will be stored """
        return self._destination

    @destination.setter
    def destination(self, file_path):
        """ Handling of input path """
        if os.path.isdir(path=file_path):
            self._destination = file_path
        elif os.path.exists(path=file_path):
            raise FileExistsError("Select a path, not a file")
        else:
            raise NotADirectoryError(f"{file_path} is an invalid directory")

    def tile_image(self):
        src_width, src_height = self.src_image.size
        for zoom in reversed(range(self.zoom_level + 1)):

            # Images cannot be stretched (as of currently) to a larger dimensions.
            # Confirm max width (or height) of the source image is greater than
            # (or possibly within a percentage of) the zoom_levels pixel width
            max_length = (2 ** zoom) * self.tile_size
            if max(src_width, src_height) / max_length < 0.5:
                print(f"Source Image ({src_width}x{src_height}) cannot be stretched to {max_length}. "
                      f"Reducing zoom_level {zoom} to {zoom - 1}")
                zoom -= 1
                continue
            else:
                print(f"Source Image({src_width}x{src_height}). Result Image({max_length}x{max_length})")
                scaled_to_tile_image = self.scale_image_to_tile(zoom=zoom)
                # scaled_to_tile_image.show()  # DEBUG

                # Cut image into pieces
                self.tilerize(scaled_image=scaled_to_tile_image, zoom=zoom)

    def scale_image_to_tile(self, zoom: int):
        """
            Scales image for desired zoom level

            Image scaling is based on smallest tile size (256) multiply by the exponent of the zoom level

            :returns tile_copy: A full-sized tile of equal dimension (ie. 256x256, 512x512)
        """
        if zoom < 0:
            print("Zoom level needs to be more than 0")
            return

        dimension = (2 ** zoom) * self.tile_size
        print(f"Scaling image to zoom level: {zoom} - Image dimensions: {dimension}x{dimension}")

        # Create base transparent background
        trans_background = self.create_background(width=dimension, height=dimension, color=self.background_color)

        # Scale image to highest dimension
        scaled_image = self.src_image
        scaled_image.thumbnail((dimension, dimension))

        # Draw scaled image onto transparent background
        tile_copy = trans_background.copy()

        # Offset to (center, center)
        offset = ((tile_copy.width - scaled_image.width) // 2, (tile_copy.height - scaled_image.height) // 2)
        tile_copy.paste(scaled_image, offset)

        return tile_copy

    def tilerize(self, scaled_image: Image.Image, zoom: int):
        """ Break image into equal-sized tiles. Default to 256px """
        width, height = scaled_image.width, scaled_image.height

        # Check to see that image can be split into even parts
        max_length = (2 ** zoom) * self.tile_size
        can_tile = True if max_length == width and max_length == height else False
        if can_tile is False and self.zoom_level != 0:
            raise ArithmeticError(f"Zoom level and image height/width mismatching...\n "
                                  f"TODO: Add ability to just use scale_image_to_tile method")

        # Gather each tile's origin point - relative (0, 0) point
        origin_points = []
        for col in range(2 ** zoom):
            for row in range(2 ** zoom):
                # Crop for each section
                origin_points.append((col, row))

        # Traverse through (Top,Left) points throughout the grid
        destination = os.path.join(self.destination, f"{zoom}")
        for col, row in origin_points:
            # Create column folder if doesn't exist
            col_dir = os.path.join(destination, f"{col}")
            Path(col_dir).mkdir(parents=True, exist_ok=True)

            start_pos = (col * self.tile_size, row * self.tile_size)  # Left & Top
            end_pos = ((col + 1) * self.tile_size, (row + 1) * self.tile_size)  # Right and Bottom

            cropped_image = scaled_image.crop(box=(start_pos + end_pos))
            cropped_image.save(os.path.join(col_dir, f"{row}.png"))

    @staticmethod
    def create_background(width, height, color) -> Image.Image:
        """ Helper function for creating a transparent tile """
        return Image.new(mode='RGBA', size=(width, height), color=color)
