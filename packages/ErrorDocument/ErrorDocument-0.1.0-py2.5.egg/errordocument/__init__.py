"""\
Error documents service
"""

import logging

from bn import AttributeDict, absimport
from configconvert.internal import eval_import

log = logging.getLogger(__name__)

class ErrorDocumentService(object):

    def __init__(self, intercept_codes, render=None):
        self.intercept_codes=intercept_codes
        self.render = render

    @staticmethod
    def config(flow, name):
        if not flow.config.option.has_key(name):
             render = absimport(
                 flow.config.app.package+'.framework.service'
             ).render
             if flow.config.app.debug:
                  intercept_codes=[400, 401, 403, 404, 405]
             else:
                  intercept_codes=[400, 401, 403, 404, 405, 500]
        else:
            try:
                intercept_codes = [
                    int(x) for x in \
                       flow.config.option[name]['intercept_codes']
                ]
            except:
                raise Exception(
                    "The %s.intercept_codes config option is invalid"
                )
            render = eval_import(flow.config.option[name]['render'])
        flow.config[name] = AttributeDict(
            dict(intercept_codes=intercept_codes, render=render)
        )
        return flow.config[name]

    @staticmethod
    def create(flow, name, config=None):
        if config is None:
            conifg = ErrorDocumentService.config(flow, name)
        return ErrorDocumentService(config.intercept_codes, config.render)

    def start(self, flow, name):

        def render(code=None, message=None, status=None):
            if status is None:
                status = flow.wsgi.status
            parts = status.split(' ')
            if code is None:
                code = int(parts[0])
            if message is None:
                message = ' '.join(parts[1:])
            if self.render:
                flow[name]['status_code'] = code
                flow[name]['status_message'] = message
                self.render(flow)
            else:
                # Display the error document
                flow.wsgi.status = '500 Internal Server Error'
                flow.wsgi.headers = [('Content-type', 'text/html')]
                flow.wsgi.response = ['''
<html>
<head><title>%(status)s</title></head>
<body>
<h1>Error %(code)s</h1>
<p>%(message)s</p>
</body>     
</html>'''%dict(status=status, code=code, message=message)]
            
        flow[name] = AttributeDict()
        flow[name]['render'] = render

    def stop(self, flow, name):
        try:
            if int(flow.wsgi.status.split(' ')[0]) in self.intercept_codes:
                flow[name].render()
        except:
            if flow.config.app.debug is True:
                raise
            else:
                raise Exception('Error generating error document')

