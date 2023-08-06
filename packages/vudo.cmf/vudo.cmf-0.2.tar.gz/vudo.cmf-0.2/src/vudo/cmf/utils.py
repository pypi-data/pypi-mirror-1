from datetime import datetime
from urllib import unquote

def get_action_from_request(request):
    return unquote(request.environ.get('PATH_INFO').split('/')[-1]).lstrip('@')

class datetimedict(datetime):
    @classmethod
    def fromdatetime(self, dt):
        return datetimedict(
            dt.year, dt.month, dt.day,
            dt.hour, dt.minute, dt.second)
        
    def __getitem__(self, key):
        """Standard `strftime()` substitutions."""

        try:
            key = str(key)
        except UnicodeDecodeError:
            raise KeyError(key)
        
        result = self.strftime("%"+str(key))
        
        if result == "":
            raise KeyError(key)

        return result

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

