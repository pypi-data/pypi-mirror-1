import utils

from vudo.cmf import MessageFactory as _

class Metadata(object):
    def __init__(self, context):
        self.context = context

    def format_creation_date(self, long_format=False):
        mapping = utils.datetimedict.fromdatetime(
            self.context.created)
        if long_format:
            return _(u"$B %e, %G @ $r", mapping=mapping)
        else:
            return _(u"$M/$d-$g @ $r", mapping=mapping)

    def __call__(self, name, *args, **kwargs):
        return getattr(self, name)(*args, **kwargs)
