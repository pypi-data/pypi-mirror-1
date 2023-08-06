# Monkey patch error_log to also log the error number
import sys

from Products.SiteErrorLog.SiteErrorLog import SiteErrorLog

from logging import getLogger
logger = getLogger('Products.errornumber')

original_copy_to_zlog = SiteErrorLog._do_copy_to_zlog

def _do_copy_to_zlog(self, now, strtype, url, tb_text):
    # Grab the error number from the calling frame
    entry_id = sys._getframe(1).f_locals['entry_id']
    url = '%s %s' % (entry_id, url)
    original_copy_to_zlog(self, now, strtype, url, tb_text)

SiteErrorLog._do_copy_to_zlog = _do_copy_to_zlog
logger.info('Applied patch version 1.1')

# Required for Zope2 products
def initialize(context):
    pass
