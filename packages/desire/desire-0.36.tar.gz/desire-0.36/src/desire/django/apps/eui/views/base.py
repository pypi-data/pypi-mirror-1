import desire.django.settings.main
from dm.view.base import SessionView

class DesireView(SessionView):

    majorNavigation = []

    def __init__(self, *args, **kwds):
        super(DesireView, self).__init__(*args, **kwds)

    def setMajorNavigationItems(self):
        items = []
        items.append({'title': 'Walks', 'url': '/walks/'})
        items.append({'title': 'Collections', 'url': '/collections/'})
        items.append({'title': 'Goals', 'url': '/goals/'})
        items.append({'title': 'Processes', 'url': '/processes/'})
        items.append({'title': 'Events', 'url': '/events/'})
        items.append({'title': 'Stories', 'url': '/stories/'})
        items.append({'title': 'Requirements', 'url': '/requirements/'})
        items.append({'title': 'Products', 'url': '/products/'})
        self.majorNavigation = items

