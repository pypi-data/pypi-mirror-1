import Products.Five.component.interfaces
import five.localsitemanager


def ensureObjectIsSite(obj):
    # make obj a site
    if Products.Five.component.interfaces.IObjectManagerSite.providedBy(obj):
        return
    five.localsitemanager.make_objectmanager_site(obj)


def initialize(context):
    # context is a ProductContext, we need the zope2-root
    app = context._ProductContext__app
    ensureObjectIsSite(app)
