from plone.app.viewletmanager.manager import OrderedViewletManager

class HiddenViewletManager(OrderedViewletManager):

    def filter(self, viewlets):
        # Returns empty list to hide all viewlets

        return []