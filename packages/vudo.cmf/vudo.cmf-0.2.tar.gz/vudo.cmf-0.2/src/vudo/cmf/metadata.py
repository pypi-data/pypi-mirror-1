import utils

from vudo.cmf import MessageFactory as _

class Metadata(object):
    def __init__(self, context):
        self.context = context

    def format_creation_date(self, long_format=False):
        date = self.context.created
        mapping = utils.datetimedict.fromdatetime(date)
            
        if long_format:
            format = "$B $e, $G @ $r"
        else:
            format = "$x @ $r"
            
        return _(
            format,
            default=date.strftime(format.replace('$', '%')),
            mapping=mapping)

    def __call__(self, name, *args, **kwargs):
        return getattr(self, name)(*args, **kwargs)
