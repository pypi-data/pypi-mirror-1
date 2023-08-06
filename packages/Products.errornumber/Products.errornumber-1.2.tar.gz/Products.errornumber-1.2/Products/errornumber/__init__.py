# Monkey patch error_log to also log the error number
import sys
import inspect

from Products.SiteErrorLog.SiteErrorLog import SiteErrorLog

from logging import getLogger
logger = getLogger('Products.errornumber')

original_copy_to_zlog = SiteErrorLog._do_copy_to_zlog

if 'entry_id' in inspect.getargspec(original_copy_to_zlog)[0]:
    logger.warn(
        'Products.errorlog is no longer required for this version of Zope. '
        'You can safely un-install this product.')

else:
    def _do_copy_to_zlog(self, now, strtype, url, tb_text):
        # Grab the error number from the calling frame
        entry_id = sys._getframe(1).f_locals['entry_id']
        url = '%s %s' % (entry_id, url)
        original_copy_to_zlog(self, now, strtype, url, tb_text)

    SiteErrorLog._do_copy_to_zlog = _do_copy_to_zlog
    logger.info('Applied patch version 1.2')

# Required for Zope2 products
def initialize(context):
    pass
