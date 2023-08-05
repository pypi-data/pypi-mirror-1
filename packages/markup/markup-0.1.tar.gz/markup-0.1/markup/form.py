import markup
from cStringIO import StringIO

class Form(object):
    """a simple class for HTML forms"""

    def __init__(self, method='post', action=None, submit='Submit'):
        self.method = method
        self.action = action
        self.submit = submit
        self.elements = []

    def __call__(self, errors=None):
        """render the form"""
        retval = StringIO()
        print >> retval

        # print the form as a table
        table = [ [ '%s:' % element['name'], element['html'] ]
                  for element in self.elements ]
        if errors:
            for row, element in zip(table, self.elements):
                error = errors.get(element['name'], '')
                if error:
                    error = markup.div(error, **{ 'class': 'error' })
                row.append(error)
            
        print >> retval, markup.tablify(table)

        # each form has a submit button
        # XXX this should probably be more customizable
        print >> retval, markup.input(None, type='submit', name='submit',
                                      value=self.submit)

        args = { 'method': self.method,
                 'enctype': 'multipart/form-data'}
        if self.action is not None:
            args['action'] = self.action            
        return markup.form(retval.getvalue(), **args)

    def validate(self, post):
        """validate the form from the (POST) data
        post should be a dictionary
        returns a dictionary of errors (empty dict == success)
        validator functions can denote failure in three ways:
        * raise an exception (currently any[!])
        * return a string -- assumed to be an error string
        * return False -- the error
        """

        errors = {}

        def add_error(name, error):
            if not errors.has_key(name):
                errors[name] = []
            errors[name].append(error)

        for element in self.elements:
            name = element['name']
            for validator in element['validators']:
                try:
                    validation = validator(post.get(name))
                except Exception, e: # horrible!
                    add_error(name, str(e))
                    continue
                if isinstance(validation, basestring):
                    # error string
                    add_error(name, validation)
                elif validation == False:
                    add_error(name, "Illegal value for %s" % name)
                    
        return errors

    ### functions to add form elements
    # each of these should be decorated to have:
    # * a name/label
    # * a validator (optional)
    # (depending on type, an additional validator may be implied)

    def textfield(self, name):
        return markup.input(None, type='text', name=name)

    def password(self, name):
        return markup.input(None, type='password', name=name)

    def file_upload(self, name):
        return markup.input(None, type='file', name=name)

    def menu(self, name, items):
        # first item is selected by default
        retval = '\n'.join([ markup.option(item) for item in items])
        return markup.select('\n%s\n' % retval, name=name)
    
    def add_element(self, func, name, *args, **kwargs):
        if isinstance(func, basestring):
            func = getattr(self, func)
        try:
            validators = kwargs.pop('validators')
        except KeyError:
            validators = ()
        self.elements.append(dict(name=name, validators=validators,
                                  html=func(name, *args, **kwargs)))
