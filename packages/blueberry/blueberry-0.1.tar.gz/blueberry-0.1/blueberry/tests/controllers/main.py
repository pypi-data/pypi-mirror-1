from blueberry import web
from blueberry import request, response

class Index(web.RequestHandler):

    def get(self):
        return """
        <form action="/" method="post">
            <input type="text" name="email" />
            <input type="submit" />
        </form>
        """

    def post(self):
        return request.POST.get('email')

class Redirect(web.RequestHandler):

    def get(self):
        self.redirect('/accept_redirect')

class AcceptRedirect(web.RequestHandler):

    def get(self):
        return self.__class__.__name__
