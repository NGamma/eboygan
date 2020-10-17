from absl import app
from absl import flags
from absl import logging
from hashlib import md5
from io import BytesIO
from json import load as json_load
from math import ceil
from os import makedirs
from os.path import isdir
from PIL import Image
from re import compile as re_compile
from requests import get
import glob

FLAGS = flags.FLAGS
flags.DEFINE_integer('size', 512, 'The size of the square images to crop.')
flags.DEFINE_integer('stride', 512, 'The stride of the sliding crop window.')
flags.DEFINE_integer('min_colors', 5, 'The minimum number of colors per crop.')
flags.DEFINE_string('input_data', 'eboy_data.json',
                    'The file containing the source image URLs.')
flags.DEFINE_string('images_dir', 'eboy-images',
                    'The image directory in which to save the crops.')
flags.DEFINE_string('image_format', 'png',
                    'The format under which to save images.')

SCALE_PATTERN = re_compile(r'^.*-(\d+)x.png$')
file_path = glob.glob("/content/drive/My Drive/gifs/***.png")

def main(_):
  for f in file_path:
    
      logging.info('Processing %s' % f)
      #image = Image.open(file).convert('RGB')
      image = Image.open(f)
      image_hash = md5(f.encode()).hexdigest()

      # Resize to pixel size of 1, if needed.
      scale_match = SCALE_PATTERN.match(f)
      if scale_match:
          scale = int(scale_match.group(1))
          logging.warning('Resizing by %dx' % scale)
          image = image.resize((image.width // scale,
                                image.height // scale), Image.NEAREST)

      # Divide the image into squares. If it doesn't evenly divide, shift
      # the last crops in to avoid empty areas.
      for y in range(ceil(image.height / FLAGS.stride)):
          y_min = y * FLAGS.stride
          y_max = y * FLAGS.stride + FLAGS.size

          if y_max > image.height:
              y_max = image.height
              y_min = y_max - FLAGS.size

          for x in range(ceil(image.width / FLAGS.stride)):
              x_min = x * FLAGS.stride
              x_max = x * FLAGS.stride + FLAGS.size

              if x_max > image.width:
                  x_max = image.width
                  x_min = x_max - FLAGS.size

              # Create the cropped image.
              crop = image.crop((x_min, y_min, x_max, y_max))

              # Discard predominantly empty crops.
              colors = crop.getcolors()
              if colors and len(colors) < FLAGS.min_colors:
                  logging.warning('Skipping empty crop')
                  continue

              # Save the image
              name = '%s/%s_%d_%d.%s' % (FLAGS.images_dir, image_hash, y,
                                         x, FLAGS.image_format)
              crop.save(name, FLAGS.image_format)
              logging.info('Saved %s' % name)


if __name__ == '__main__':
    app.run(main)
