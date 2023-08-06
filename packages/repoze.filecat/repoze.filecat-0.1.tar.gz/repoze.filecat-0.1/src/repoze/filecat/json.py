from webob import Response
import jsonlib

class JSONResponse(Response):
    def __init__(self, data, **kwargs):
        Response.__init__(self, content_type="text/json", **kwargs)
        self.body = jsonlib.write(data)
