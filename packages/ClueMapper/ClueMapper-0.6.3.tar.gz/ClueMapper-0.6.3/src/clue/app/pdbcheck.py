import sys
import pdb
import logging
logger = logging.getLogger('cluemapper')


class PDBCheckFilter(object):
    """Middleware for handling debugging.

      >>> import traceback, sys
      >>> from clue.tools.testing import Mock
      >>> def debug(tb):
      ...     print 'Error correctly raised'
      >>> f = PDBCheckFilter(lambda x,y: None, None)
      >>> f.debug = debug
      >>> f.logger = Mock(error=lambda x: None)
      >>> f(None, None)

      >>> def raiseerr(x, y): raise ValueError('test error')
      >>> f.app = raiseerr
      >>> f(None, None)
      Error correctly raised

    """

    debug = pdb.post_mortem
    logger = logger

    def __init__(self, app, global_conf):
        self.app = app
        self.global_conf = global_conf

    def __call__(self, environ, start_response):
        try:
            return self.app(environ, start_response)
        except:
            self.logger.error('Caught error, starting post-mortem debugger')
            tb = sys.exc_info()[2]
            self.debug(tb)

make_filter = PDBCheckFilter
