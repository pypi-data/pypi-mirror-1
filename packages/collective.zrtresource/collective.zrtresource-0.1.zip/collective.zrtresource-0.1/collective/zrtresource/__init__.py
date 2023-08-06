# monkey patch
from collective.zrtresource.zrtresource import ZRTFileResource
import z3c.zrtresource.zrtresource
z3c.zrtresource.zrtresource.ZRTFileResource = ZRTFileResource
