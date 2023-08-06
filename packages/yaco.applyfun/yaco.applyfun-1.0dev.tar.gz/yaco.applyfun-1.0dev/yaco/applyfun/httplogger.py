"""
This has been extracted from the excellent ZSyncer product, by Paul M. Winkler and contributors.
It basically allows to send log messages from the server to the browser.
"""

import time
import logging
from DocumentTemplate.DT_Util import html_quote


# Colors for the UI
color_200 = 'green'
color_error = 'red'

class TextMsg:

    """For logging & output of arbitrary text.
    """

    color = 'black'
    status = 200

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return str(self.msg)

    def html(self):
        return '<div style="color: %s">%s</div>\n' % (self.color,
                                                      html_quote(self.msg))


class StatusMsg(TextMsg): #, Acquisition.Implicit):

    """For logging & output of remote call results.
    """

    def __init__(self, msg, status, color=None):
        """msg may be a text string or a TextMsg.
        """
        status = int(status)
        if isinstance(msg, TextMsg):
            msg = msg.msg
        self.status = status
        if color:
            self.color = color
            self.msg = msg
        elif status == 200:
            self.color = color_200
            if not msg.startswith('OK'):
                msg = 'OK: %s' % msg
            self.msg = msg
        else:
            self.color = color_error
            self.msg = msg

    def __eq__(self, other):
        # Useful for testing.
        return (other.msg == self.msg and other.status == self.status)

    def __repr__(self):
        # Useful for testing.
        return '%s("%s", %s)' % (self.__class__.__name__,
                               self.msg, self.status)

# This is necessary in order to use the Msg classes in untrusted code.
from Products.PythonScripts.Utility import allow_class
allow_class(StatusMsg)
allow_class(TextMsg)

class HTTPLogger(object):
    
    def __init__(self, context=None, REQUEST=None):
        self.REQUEST = REQUEST
        self.log = logging
        self.context = context
        self.remote = REQUEST and True or False

    def get_time(self):
        # Get time for logging.
        # Could be done using DateTime, but i think I want to fiddle this.
        return time.asctime(time.localtime(time.time()))

    def make_msg(self, msg, status=200, color=None):
        """
        From a string, make a StatusMsg
        """
        if isinstance(msg, StatusMsg):
            return msg
        return StatusMsg(msg, status, color)

    def do_messages(self, msgs):
        """Log a list of messages, and if there is a REQUEST, do an
        html display.
        """
        self.msg_header()
        processed_msgs = []
        for m in msgs:
            if isinstance(m, StatusMsg):
                processed_msgs.append(m)
            else:
                # Presumably something we can wrap in a StatusMsg.
                processed_msgs.append(StatusMsg(m))
        for m in processed_msgs:
            self.do_one_msg(m)
        self.msg_footer()
        return processed_msgs

    def msg_header(self):
        '''Writes log and/or html info at beginning of a sync.
        '''
        if self.remote:
            # Be sure we have enough content-length... overestimate.
            self.REQUEST.RESPONSE.setHeader('content-type', 'text/html')
            head ='<html><body>'
            self.REQUEST.RESPONSE.write(head)
        self.log.info(' -------  Started logging  -------')

    def msg_footer(self):
        if self.remote:
            url_back = self.context and self.context.absolute_url() or \
                                                       'javascript:history.back(2)'
            foot = '''<div>
                <a href="%s">BACK TO CONTEXT</a>
                </div>
                </body></html>
            ''' % url_back
            self.REQUEST.RESPONSE.write(foot)
        self.log.info(' -------  Done logging  -------  ')

    def do_one_msg(self, msg):
        """Log and/or display a single Msg.
        """
        msg = self.make_msg(msg)
        if self.remote:
            html = msg.html()
            self.REQUEST.RESPONSE.write(str(html))
            self.REQUEST.RESPONSE.flush()
        self.log.info(msg.msg)
