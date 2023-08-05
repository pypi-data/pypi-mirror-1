"""Peforce spec-based form handling classes."""

__all__ = ['SpecError', 'ParseError', 'Form']

from perforce.api import SpecError, ParseError

class Form(object):
    """A Perforce form object.

    A form consists of a collection of named fields, each with a particular
    type and format. The form object handles parsing and formatting of Perforce
    forms to/from Python values.
    
    The field values are accessed using dictionary notation.
    ie. C{form['FieldName']}
    
    The field attributes are accessed using attribute notation.
    ie. C{form.FieldName}
    """

    __slots__ = ['spec', 'values']

    def __init__(self, specdef, data):
        """Construct a Form object from the specdef and form data.

        @param specdef: The Perforce form specification string.
        Typically obtained from the Perforce server via the C{outputStat()}
        method.
        @type specdef: C{str}

        @param data: The formatted Perforce form data to parse.
        @type data: C{str}

        @raise SpecError: If the C{specdef} is not a valid Perforce form
        specification.
        @raise ParseError: If the form C{data} is incorrectly formatted or
        references invalid fields.
        """

        from perforce.api import Spec

        spec = Spec(specdef)
        if isinstance(data, dict):
            # Perforce 2005.2 and later sends us a dictionary of field values
            # instead of a text representation of the form.
            # Need to manually format the dictionary back to a text form
            # that can be parsed by the spec object into the PyPerforce
            # dictionary format using lists and tuples rather than a basic
            # string for each line.
            formLines = []
            for field in spec:
                elem = spec[field]
                if elem.isSingle():
                    if field in data:
                        formLines.append('%s:\t%s' % (field, data[field]))
                        formLines.append('')
                else:
                    fieldLines = []
                    if elem.isList():
                        i = 0
                        while '%s%i' % (field, i) in data:
                            key = '%s%i' % (field, i)
                            fieldLines.append('\t%s' % data[key])
                            i += 1
                    else:
                        if field in data:
                            textLines = data[field].split('\n')
                            fieldLines.extend(['\t%s' % x for x in textLines])
                        
                    if fieldLines:
                        formLines.append('%s:' % field)
                        formLines.extend(fieldLines)
                        formLines.append('')

            data = '\n'.join(formLines)
        
        object.__setattr__(self, 'spec', spec)
        object.__setattr__(self, 'values', spec.parse(data))

    def __getattribute__(self, fieldName):
        """Return the details of a particular field in a
        L{perforce.api.SpecElem} value.

        @raise AttributeError: if there is no such field.
        """
        spec = object.__getattribute__(self, 'spec')
        
        if fieldName not in spec:
            raise AttributeError("No such field '%s'" % fieldName)

        return spec[fieldName]

    def __setattr__(self, fieldName, value):
        """Setting of field details is not allowed.

        @raise AttributeError: Unconditionally.
        """
        raise AttributeError("Details of field '%s' cannot be changed" %
                             fieldName)

    def __delattr__(self, fieldName):
        """Deleting field details is not allowed.

        @raise AttributeError: Unconditionally.
        """
        raise AttributeError("Details of field '%s' cannot be deleted" %
                             fieldName)

    def __getitem__(self, fieldName):
        """Return the value of a particular field.

        @return: The value of the field.
          The type of the field can be determined from the field's
          corresponding L{perforce.api.SpecElem}. Multi-word fields
          are stored as C{tuple}s, list fields are stored as C{list}s
          and single-line fields or multi-line text fields are stored
          as C{str}s.

        @raise KeyError: if there is no such field.

        @see: L{__setitem__}
        """
        spec = object.__getattribute__(self, 'spec')
        values = object.__getattribute__(self, 'values')

        # Raises an exception if no such field
        elem = spec[fieldName]

        if fieldName not in values:
            if elem.isList():
                values[fieldName] = []
            else:
                values[fieldName] = None

        return values[fieldName]

    def __setitem__(self, fieldName, value):
        """Set the value of a particular field.

        @raise KeyError: if there is no such field.

        @see: L{__getitem__}, L{__delitem__}
        """
        spec = object.__getattribute__(self, 'spec')
        values = object.__getattribute__(self, 'values')

        # Raises an exception if no such field
        elem = spec[fieldName]

        # TODO: Perform some type checking to make sure the value has
        #       the right format. An invalid value will show up later
        #       as a silent failure when rendering the form.
        
        values[fieldName] = value

    def __delitem__(self, fieldName):
        """Clear the value of a particular field.

        @raise KeyError: if there is no such field.

        @see: L{__setitem__}
        """
        spec = object.__getattribute__(self, 'spec')
        values = object.__getattribute__(self, 'values')

        # Raises an exception if no such field
        elem = spec[fieldName]

        if fieldName in values:
            del values[fieldName]

    def __str__(self):
        """Format the form's values as a Perforce form.

        @note: Fields with values that do not have the correct Python type
        (C{list}, C{tuple}, C{str} etc) will be treated as though the field
        has no value associated.
        """
        spec = object.__getattribute__(self, 'spec')
        values = object.__getattribute__(self, 'values')
        return spec.format(values)

    def __contains__(self, fieldName):
        """Query whether a particular field exists in this form.

        Enables code such as::
          | if 'FieldName' in form:
          |   value = form['FieldName']
        """
        spec = object.__getattribute__(self, 'spec')
        return fieldName in spec

    def __len__(self):
        """Query the number of fields in this form.

        @rtype: C{int}
        """
        return len(object.__getattribute__(self, 'spec'))

    def __iter__(self):
        """Iterate over the names of the fields in this form.

        Enables code such as::
          | for fieldName in form:
          |   print form[fieldName]
        """
        return iter(object.__getattribute__(self, 'spec'))
