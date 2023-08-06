from Products.Five import BrowserView
from datetime import datetime

class EventTemplateSender(BrowserView):

    def __call__(self, event_code, headers):
        now = datetime.now()
        return self.index(event_code=event_code,
                          headers=headers,
                          date=now.ctime(),
                          )
