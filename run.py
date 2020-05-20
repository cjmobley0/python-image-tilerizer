import os
from src.tilerizer import Tilerizer

img_path = os.path.join(os.getcwd(), "IMAGE_HERE")
destination = os.path.join(os.getcwd(), 'results')
img = Tilerizer(source_image=img_path, zoom_level=5, destination=destination).tile_image()
