__id__= '$Id: plastic.py 97 2007-05-29 15:51:00Z eddie $'
__docformat__ = 'restructuredtext en'

from astrogrid import acr
from decorators import deprecated

# For compatibility
@deprecated
def broadcast(*args, **kwargs):
	return acr.plastic.broadcast(*args, **kwargs)
