from Products.Five import BrowserView
from yaco.applyfun.httplogger import HTTPLogger


class HTTPLoggingBrowserView(BrowserView):

    def __init__(self, context, request):
        super(HTTPLoggingBrowserView, self).__init__(context, request)
        self.logger = HTTPLogger(context=context,
                                 REQUEST=request)

    def context():
        def get(self):
            return self._context[0]
        def set(self, context):
            self._context = [context]
        return property(get, set)
    context = context()
