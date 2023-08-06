import re

from zope.schema import TextLine
from zope.schema.interfaces import ValidationError

from zope.i18nmessageid import MessageFactory
_ = MessageFactory("largeblue")


_valid_characters = re.compile(r"^[a-z0-9_\.]+$").match
_starts_with_lowercase_letter = re.compile(r"^[a-z]+").match


def _is_valid_obj_name(n):
    return _valid_characters(n) and _starts_with_lowercase_letter(n)



class InvalidObjectName(ValidationError):
    __doc__ = _('must only contain lower case letters, numbers, full stops \
        and underscores and must start with a letter.'
    )



class ObjectName(TextLine):
    def _validate(self, value):
        # normal textline validation
        super(ObjectName, self)._validate(value)
        # now test to see it it matches our requirements
        if _is_valid_obj_name:
            return ''
        raise InvalidObjectName()
    

