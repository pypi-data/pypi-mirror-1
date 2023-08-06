import re
from Products.validation.interfaces import ivalidator

class PartialUrlValidator:
    __implements__ = (ivalidator,)
    def __init__(self, name):
        self.name = name
    def __call__(self, value, *args, **kwargs):
        # field gets passed in via kwargs
        if '://' not in value:
            widget = kwargs.get('field').widget
            default_p = getattr(widget,'default_protocol','http')
            value = default_p + '://' + value
        pattern = re.compile(r'(ht|f)tps?://[^\s\r\n]+')
        m = pattern.match(value)
        if not m:
            return ("Validation failed(%s): value is %s"%(self.name,
                repr(value)))
        return 1
