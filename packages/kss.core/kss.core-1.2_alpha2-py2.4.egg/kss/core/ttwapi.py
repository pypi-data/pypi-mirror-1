from kss.core import KSSView
from kss.core.interfaces import IKSSView
from zope.app.component.hooks import getSite

def startKSSCommands(context, request):
    view = KSSView(context, request)
    view.__before_publishing_traverse__(context, request)
    return view

def getKSSCommandSet(name):
    view = retrieveView()
    cs = view.getCommandSet(name)
    return cs

def renderKSSCommands():
    view = retrieveView()
    return view.render()

def retrieveView():
    #because the view registers itself as a site,
    #we can retrieve it...
    site = getSite()
    if not IKSSView.providedBy(site):
        raise LookupError("You haven't initialized the KSS response yet, "
                          "do so by calling startKSSCommands(context, request).")
    return site


