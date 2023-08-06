""" Zope3 view that allows to apply functions defined in walker_funcs
    to the context and each object in its contained hyerarchy,
    or to the objects selected through a catalog query
"""
import logging
import transaction
from Products.CMFCore.utils import getToolByName

from yaco.applyfun.browser import HTTPLoggingBrowserView

from yaco.applyfun.config import functions
logger = logging.getLogger('Applyfun')

class Walker(HTTPLoggingBrowserView):

    def start_walking(self):
        if self.request.get('doit', False) and \
           self.request.get('function') != 'nada':
            #
            function = self.request.get('function')
            email = self.request.get('email')
            kwargs = self.request.get('kwargs', '')
            if email:
                self.msgs = ['messages for function %s with args %s' % (function, kwargs)]
            else:
                self.msgs = None
            if kwargs:
                kwargs = eval(kwargs)
            else:
                kwargs = {}
            self._savepoint_interval = int(self.request.get('savepoint_interval'))
            self._counter = 0
            catalog_query = self.request.get('catalog_query')
            self.logger.msg_header()
            if catalog_query:
                catalog_query = eval(catalog_query)
                pc = getToolByName(self.context, 'portal_catalog')
                brains = pc(catalog_query)
                for b in brains:
                    self._counter += 1
                    ob = b.getObject()
                    functions[function](ob, logger=self, **kwargs)
                    if self._savepoint_interval and self._counter % self._savepoint_interval == 0:
                        msg = self.logger.make_msg("Savepoint for function %s" % function, color='blue')
                        self.logger.do_one_msg(msg)
                        # Create a savepoint when the time has come
                        transaction.savepoint()
            else:
                self.walk(self.context, function, kwargs)
            self.logger.msg_footer()
            if self.msgs:
                mh = getToolByName(self.context, 'MailHost')
                plone_utils = getToolByName(self.context, 'plone_utils')
                portal_url = getToolByName(self.context, 'portal_url')
                encoding = plone_utils.getSiteEncoding()
                mFrom = portal_url.getPortalObject().getProperty('email_from_address')
                mh.secureSend('\n'.join(self.msgs), email, mFrom, subject=self.msgs[0], subtype='plain', charset=encoding, debug=False, From=mFrom)
            return True
        else:
            return False

    def walk(self, ob, function, kwargs):
        # Everytime an object is encountered, count one up
        self._counter = self._counter + 1
        
        # Call the function on the object
        functions[function](ob, logger=self, **kwargs)
        
        # Use savepoints if this is demanded
        if self._savepoint_interval:
            # Savepoints are used when the savepoint interval set.
            if self._counter % self._savepoint_interval == 0:
                msg = self.logger.make_msg("Savepoint for function %s" % function, color='blue')
                self.logger.do_one_msg(msg)
                # Create a savepoint when the time has come
                transaction.savepoint()
        else:
            #If the savepoint interval is set to 0, no savepoints are used.
            pass

        if ob.isPrincipiaFolderish:
            for o in ob.objectValues():
                self.walk(o, function, kwargs)
    
    def get_functions(self):
        return functions

    def log(self, msg, color='green'):
        message = self.logger.make_msg(msg, color=color)
        self.logger.do_one_msg(message)
        if self.msgs:
            self.msgs.append(msg)

