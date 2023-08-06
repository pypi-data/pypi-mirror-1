from blueberry.tests.controllers import main
from blueberry.tests.controllers import tags
from blueberry.tests.controllers import forms

urls = [
    (r'/', main.Index),
    (r'/redirect', main.Redirect),
    (r'/accept_redirect', main.AcceptRedirect),
    (r'/tags/([^/]+)', tags.Show),
    (r'/forms', forms.Index)
]
