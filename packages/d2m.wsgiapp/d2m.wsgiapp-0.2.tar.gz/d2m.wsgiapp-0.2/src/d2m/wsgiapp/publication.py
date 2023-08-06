import os.path
from zope import interface
from zope import component
from zope.app.appsetup import appsetup
from zope.app.folder.interfaces import IRootFolder
from zope.publisher.browser import setDefaultSkin
from zope.publisher.paste import Application
from grok.publication import GrokBrowserPublication

def app_factory(global_config, publication, **options):
    cfg=appsetup.config(os.path.join(global_config['here'],'site.zcml'))
    return Application(global_config, publication, **options)

class ApplicationRoot(dict): 
    interface.implements(IRootFolder)

class BrowserPublication(GrokBrowserPublication):

    def __init__(self,global_config, **options):
        self._app = ApplicationRoot()

    def getApplication(self, request):
        setDefaultSkin(request)
        return self._app
