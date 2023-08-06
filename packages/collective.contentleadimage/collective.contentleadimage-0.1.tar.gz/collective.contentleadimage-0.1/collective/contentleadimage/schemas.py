from zope import schema
from StringIO import StringIO
from zope.schema._bootstrapinterfaces import WrongType
import PIL

class ImageLine(schema.TextLine):

    def _validate(self, value):
        """ Overwrites validator for FileWidget  """
        try:
            image = PIL.Image.open(StringIO(value))
            del image
        except IOError, e:
            raise WrongType(e)