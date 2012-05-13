from StringIO import StringIO
from PIL import Image

def resize(orig, size):
  image = Image.open(StringIO(orig))
  image.thumbnail((size, size), Image.ANTIALIAS)
  output = StringIO()
  image.save(output, "JPEG")
  data = output.getvalue()
  return data