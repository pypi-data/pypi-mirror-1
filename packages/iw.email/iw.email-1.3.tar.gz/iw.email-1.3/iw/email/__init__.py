import logging
from iw.email.mail import MultipartMail
from iw.email.templates import BasicMailTemplate

log = logging.getLogger(__name__)

try:
    import Cheetah
except ImportError:
    log.warn('Cheetah is not available')
else:
    from iw.email.cheetah_template import *

try:
    import mako
except ImportError:
    log.warn('Mako is not available')
else:
    from iw.email.mako_template import *

