from plone.app.portlets.browser.manage import ManageContextualPortletsViewlet as base

class ManageContextualPortletsViewlet(base):
    """Viewlet for @@manage-portlets view to make portlets inserted via this
    viewlet editable.

    And this viewlet fix problem with kss edit. It just add __name__ attribute
    which is required for ajax functionality.
    """

    def __init__(self, context, request, view, manager):
        super(ManageContextualPortletsViewlet, self).__init__(context, request, view, manager)
        self.__name__ = view.__name__

