# Monkey patch error_log to also log the error number
from Products.SiteErrorLog.SiteErrorLog import *
from Products.SiteErrorLog.SiteErrorLog import _rate_restrict_pool
from Products.SiteErrorLog.SiteErrorLog import _rate_restrict_period
from Products.SiteErrorLog.SiteErrorLog import _rate_restrict_burst

from logging import getLogger
logger = getLogger('Products.errornumber')

def raising(self, info):
    """Log an exception.

    Called by SimpleItem's exception handler.
    Returns the url to view the error log entry
    """
    try:
        now = time.time()
        try:
            tb_text = None
            tb_html = None

            strtype = str(getattr(info[0], '__name__', info[0]))
            if strtype in self._ignored_exceptions:
                return

            if not isinstance(info[2], basestring):
                tb_text = ''.join(
                    format_exception(*info, **{'as_html': 0}))
                tb_html = ''.join(
                    format_exception(*info, **{'as_html': 1}))
            else:
                tb_text = info[2]

            request = getattr(self, 'REQUEST', None)
            url = None
            username = None
            userid   = None
            req_html = None
            try:
                strv = str(info[1])
            except:
                strv = '<unprintable %s object>' % type(info[1]).__name__
            if request:
                url = request.get('URL', '?')
                usr = getSecurityManager().getUser()
                username = usr.getUserName()
                userid = usr.getId()
                try:
                    req_html = str(request)
                except:
                    pass
                if strtype == 'NotFound':
                    strv = url
                    next = request['TraversalRequestNameStack']
                    if next:
                        next = list(next)
                        next.reverse()
                        strv = '%s [ /%s ]' % (strv, '/'.join(next))

            log = self._getLog()
            entry_id = str(now) + str(random()) # Low chance of collision
            log.append({
                'type': strtype,
                'value': strv,
                'time': now,
                'id': entry_id,
                'tb_text': tb_text,
                'tb_html': tb_html,
                'username': username,
                'userid': userid,
                'url': url,
                'req_html': req_html,
                })

            cleanup_lock.acquire()
            try:
                if len(log) >= self.keep_entries:
                    del log[:-self.keep_entries]
            finally:
                cleanup_lock.release()
        except:
            LOG.error('Error while logging', exc_info=sys.exc_info())
        else:
            if self.copy_to_zlog:
                self._do_copy_to_zlog(now,strtype,str(url),tb_text,entry_id)
            return '%s/showEntry?id=%s' % (self.absolute_url(), entry_id)
    finally:
        info = None

def _do_copy_to_zlog(self,now,strtype,url,tb_text,entry_id):
    when = _rate_restrict_pool.get(strtype,0)
    if now>when:
        next_when = max(when, now-_rate_restrict_burst*_rate_restrict_period)
        next_when += _rate_restrict_period
        _rate_restrict_pool[strtype] = next_when
        LOG.error('%s %s\n%s' % (entry_id, url, tb_text.rstrip()))

# Monkey patch
SiteErrorLog.raising = raising
SiteErrorLog._do_copy_to_zlog = _do_copy_to_zlog
logger.info('Applied patch version 1.0')

# Required for Zope2 products
def initialize(context):
    pass
