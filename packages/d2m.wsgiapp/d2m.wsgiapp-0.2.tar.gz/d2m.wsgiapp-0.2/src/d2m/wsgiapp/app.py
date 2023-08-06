import grok
from zope.app.folder.interfaces import IRootFolder
import time

grok.context(IRootFolder)

class Index(grok.View):
    grok.name('index.html')

class TimeNow(grok.View):
    def render(self):
        return str(time.time())