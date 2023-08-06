from blueberry import web
from blueberry.decorators import validate
from formencode import Schema, validators

class FilteringSchema(Schema):
    filter_extra_fields = True
    allow_extra_fields = True

class IndexFormSchema(FilteringSchema):
    username = validators.String(not_empty=True)
    password = validators.String(not_empty=True)
    confirm_password = validators.String(not_empty=True)

    chained_validators = [validators.FieldsMatch('password', 'confirm_password')]

class Index(web.RequestHandler):

    def get(self):
        errors = getattr(self, 'form_errors', {})
        defaults = getattr(self, 'form_result', {})

        return """
        <p>Errors: %s</p>
        <form action="/forms" method="post">
            <input type="text" name="username" value="%s" />
            <input type="password" name="password" />
            <input type="password" name="confirm_password" />
            <input type="submit" />
        </form>
        """ % (
            '\n'.join('%s: %s' % (k, v) for k, v in errors.items()),
            defaults.get('username', '')
        )

    @validate(schema=IndexFormSchema(), error_handler='get')
    def post(self):
        return self.form_result.get('username')
