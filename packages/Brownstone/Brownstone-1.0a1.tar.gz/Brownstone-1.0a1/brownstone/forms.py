import formencode

def errors_to_dict(errors):
    """Converts a :class:`formencode.Invalid` exception into a
    dictionary of error values recursively."""

    if not errors.error_dict:
        if errors.error_list:
            lst = []
            for error in errors.error_list:
                if not error is None:
                    lst.append(errors_to_dict(error))
            return lst
        else:
            return errors.msg

    adict = errors.error_dict
    adict = dict((key, errors_to_dict(errors))
                 for key, errors in adict.iteritems())
    return adict

class Schema(formencode.Schema):
    """A :meth:`to_python` wrapper."""

    def convert(self, fallback, adict, *a):
        """Takes a fallback URL and keeps it around in case
        :meth:`formencode.Schema.to_python` raises a validation
        error."""

        try:
            # Common CSRF protection field that will trigger the field
            # not expected validation error if we don't remove it. And
            # we can't remove things from webob.NestedMultiDicts, so
            # we create a dictionary copy first.
            adict = dict(adict)
            adict.pop('nonce', None)
            return super(Schema, self).to_python(adict, *a)
        except formencode.Invalid, e:
            e.fallback = fallback
            raise e
