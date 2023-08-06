from blueberry import web

class Show(web.RequestHandler):

    def get(self, tag):
        return tag
