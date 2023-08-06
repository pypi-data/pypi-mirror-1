from desire.django.apps.eui.views.base import DesireView
from dm.view.registry import RegistryView
from dm.view.registry import RegistryListView
from dm.view.registry import RegistryCreateView
from dm.view.registry import RegistryReadView
from dm.view.registry import RegistrySearchView
from dm.view.registry import RegistryFindView
from dm.view.registry import RegistryUpdateView
from dm.view.registry import RegistryDeleteView

class FieldNames(list):

    def __init__(self, *args, **kwds):
        super(FieldNames, self).__init__(*args, **kwds)


class CollectionFields(FieldNames):

    def __init__(self, *args, **kwds):
        super(CollectionFields, self).__init__(*args, **kwds)
        self.append('description')
        self.append('processes')
        self.append('products')


class GoalFields(FieldNames):

    def __init__(self, *args, **kwds):
        super(GoalFields, self).__init__(*args, **kwds)
        self.append('description')
        self.append('processes')


class ProcessFields(FieldNames):

    def __init__(self, *args, **kwds):
        super(ProcessFields, self).__init__(*args, **kwds)
        self.append('description')
        self.append('collections')
        self.append('goals')
        self.append('events')
        self.append('links')
        self.append('backLinks')


class EventFields(FieldNames):

    def __init__(self, *args, **kwds):
        super(EventFields, self).__init__(*args, **kwds)
        self.append('description')
        self.append('processes')
        self.append('causes')
        self.append('responses')


class StoryFields(FieldNames):

    def __init__(self, *args, **kwds):
        super(StoryFields, self).__init__(*args, **kwds)
        self.append('description')
        self.append('narrative')
        self.append('handles')
        self.append('raises')
        self.append('products')
        self.append('actors')
        self.append('requirements')
        self.append('ticketUrl')


class RequirementFields(FieldNames):

    def __init__(self, *args, **kwds):
        super(RequirementFields, self).__init__(*args, **kwds)
        self.append('type')
        self.append('description')
        self.append('stories')
        self.append('satisfaction')
        self.append('dissatisfaction')
        self.append('rationale')
        self.append('fitCriterion')
        self.append('dependencies')
        self.append('conflicts')
        self.append('source')
        self.append('supportingMaterials')
        self.append('history')
        self.append('ticketUrl')


class ProductFields(FieldNames):

    def __init__(self, *args, **kwds):
        super(ProductFields, self).__init__(*args, **kwds)
        self.append('description')
        self.append('newTicketUrl')
        self.append('stories')
        self.append('collections')
        self.append('purpose')
        self.append('stakeholders')
        self.append('users')
        self.append('constraints')
        self.append('glossary')
        self.append('notes')


class BaseNavigation(object):

    def __init__(self, view):
        self.view = view

    def createMajorItem(self):
        raise Exception("Method not implemented")

    def createMinorItem(self):
        raise Exception("Method not implemented")

    def createMinorItems(self):
        raise Exception("Method not implemented")


class CollectionNavigation(BaseNavigation):

    def createMajorItem(self):
        return '/collections/'

    def createMinorItem(self):
        return ''

    def createMinorItems(self):
        items = []
        items.append(
            {'title': 'Index', 'url': '/collections/'}
        )
        items.append(
            {'title': 'Search', 'url': '/collections/search/'}
        )
        items.append(
            {'title': 'New', 'url': '/collections/create/'}
        )
        return items


class GoalNavigation(BaseNavigation):

    def createMajorItem(self):
        return '/goals/'

    def createMinorItem(self):
        return ''

    def createMinorItems(self):
        items = []
        items.append(
            {'title': 'Index', 'url': '/goals/'}
        )
        items.append(
            {'title': 'Search', 'url': '/goals/search/'}
        )
        items.append(
            {'title': 'New', 'url': '/goals/create/'}
        )
        return items


class ProcessNavigation(BaseNavigation):

    def createMajorItem(self):
        return '/processes/'

    def createMinorItem(self):
        return ''

    def createMinorItems(self):
        items = []
        items.append(
            {'title': 'Index', 'url': '/processes/'}
        )
        items.append(
            {'title': 'Search', 'url': '/processes/search/'}
        )
        items.append(
            {'title': 'New', 'url': '/processes/create/'}
        )
        return items


class EventNavigation(BaseNavigation):

    def createMajorItem(self):
        return '/events/'

    def createMinorItem(self):
        return ''

    def createMinorItems(self):
        items = []
        items.append(
            {'title': 'Index', 'url': '/events/'}
        )
        items.append(
            {'title': 'Search', 'url': '/events/search/'}
        )
        items.append(
            {'title': 'New', 'url': '/events/create/'}
        )
        return items


class StoryNavigation(BaseNavigation):

    def createMajorItem(self):
        return '/stories/'

    def createMinorItem(self):
        return ''

    def createMinorItems(self):
        items = []
        items.append(
            {'title': 'Index', 'url': '/stories/'}
        )
        items.append(
            {'title': 'Search', 'url': '/stories/search/'}
        )
        items.append(
            {'title': 'New', 'url': '/stories/create/'}
        )
        return items


class RequirementNavigation(BaseNavigation):

    def createMajorItem(self):
        return '/requirements/'

    def createMinorItem(self):
        return ''

    def createMinorItems(self):
        items = []
        items.append(
            {'title': 'Index', 'url': '/requirements/'}
        )
        items.append(
            {'title': 'Search', 'url': '/requirements/search/'}
        )
        items.append(
            {'title': 'New', 'url': '/requirements/create/'}
        )
        return items


class ProductNavigation(BaseNavigation):

    def createMajorItem(self):
        return '/products/'

    def createMinorItem(self):
        return ''

    def createMinorItems(self):
        items = []
        items.append(
            {'title': 'Index', 'url': '/products/'}
        )
        items.append(
            {'title': 'Search', 'url': '/products/search/'}
        )
        items.append(
            {'title': 'New', 'url': '/products/create/'}
        )
        return items


class DesireRegistryView(RegistryView, DesireView):

    domainClassName = ''
    manipulatedFieldNames = {
        'collections/create': CollectionFields(),
        'collections/read':   CollectionFields(),
        'collections/update': CollectionFields(),
        'collections/delete': CollectionFields(),
        'goals/create': GoalFields(),
        'goals/read':   GoalFields(),
        'goals/update': GoalFields(),
        'goals/delete': GoalFields(),
        'processes/create': ProcessFields(),
        'processes/read':   ProcessFields(),
        'processes/update': ProcessFields(),
        'processes/delete': ProcessFields(),
        'events/create': EventFields(),
        'events/read':   EventFields(),
        'events/update': EventFields(),
        'events/delete': EventFields(),
        'stories/create': StoryFields(),
        'stories/read':   StoryFields(),
        'stories/update': StoryFields(),
        'stories/delete': StoryFields(),
        'requirements/create': RequirementFields(),
        'requirements/read':   RequirementFields(),
        'requirements/update': RequirementFields(),
        'requirements/delete': RequirementFields(),
        'products/create': ProductFields(),
        'products/read':   ProductFields(),
        'products/update': ProductFields(),
        'products/delete': ProductFields(),
    }
    manipulators = {
    }
    redirectors = {
    }
    navigation = {
        'collections/list':   CollectionNavigation,
        'collections/create': CollectionNavigation,
        'collections/read':   CollectionNavigation,
        'collections/search': CollectionNavigation,
        'collections/find':   CollectionNavigation,
        'collections/update': CollectionNavigation,
        'collections/delete': CollectionNavigation,
        'goals/list':   GoalNavigation,
        'goals/create': GoalNavigation,
        'goals/read':   GoalNavigation,
        'goals/search': GoalNavigation,
        'goals/find':   GoalNavigation,
        'goals/update': GoalNavigation,
        'goals/delete': GoalNavigation,
        'processes/list':   ProcessNavigation,
        'processes/create': ProcessNavigation,
        'processes/read':   ProcessNavigation,
        'processes/search': ProcessNavigation,
        'processes/find':   ProcessNavigation,
        'processes/update': ProcessNavigation,
        'processes/delete': ProcessNavigation,
        'events/list':   EventNavigation,
        'events/create': EventNavigation,
        'events/read':   EventNavigation,
        'events/search': EventNavigation,
        'events/find':   EventNavigation,
        'events/update': EventNavigation,
        'events/delete': EventNavigation,
        'stories/list':   StoryNavigation,
        'stories/create': StoryNavigation,
        'stories/read':   StoryNavigation,
        'stories/search': StoryNavigation,
        'stories/find':   StoryNavigation,
        'stories/update': StoryNavigation,
        'stories/delete': StoryNavigation,
        'requirements/list':   RequirementNavigation,
        'requirements/create': RequirementNavigation,
        'requirements/read':   RequirementNavigation,
        'requirements/search': RequirementNavigation,
        'requirements/find':   RequirementNavigation,
        'requirements/update': RequirementNavigation,
        'requirements/delete': RequirementNavigation,
        'products/list':   ProductNavigation,
        'products/create': ProductNavigation,
        'products/read':   ProductNavigation,
        'products/search': ProductNavigation,
        'products/find':   ProductNavigation,
        'products/update': ProductNavigation,
        'products/delete': ProductNavigation,
    }


class DesireRegistryListView(DesireRegistryView, RegistryListView):
    pass

class DesireRegistryCreateView(DesireRegistryView, RegistryCreateView):
    pass

class DesireRegistryReadView(DesireRegistryView, RegistryReadView):
    pass

class DesireRegistrySearchView(DesireRegistryView, RegistrySearchView):
    pass

class DesireRegistryFindView(DesireRegistryView, RegistryFindView):
    pass

class DesireRegistryUpdateView(DesireRegistryView, RegistryUpdateView):
    pass

class DesireRegistryDeleteView(DesireRegistryView, RegistryDeleteView):
    pass


def view(request, registryPath, actionName='', actionValue=''):
    pathNames = registryPath.split('/')
    pathLen = len(pathNames)
    if not actionName:
        if pathLen % 2:
            actionName = 'list'
        else:
            actionName = 'read'
    if actionName == 'list':
        viewClass = DesireRegistryListView
    elif actionName == 'create':
        viewClass = DesireRegistryCreateView
    elif actionName == 'read':
        viewClass = DesireRegistryReadView
    elif actionName == 'search':
        viewClass = DesireRegistrySearchView
    elif actionName == 'find':
        viewClass = DesireRegistryFindView
    elif actionName == 'update':
        viewClass = DesireRegistryUpdateView
    elif actionName == 'delete':
        viewClass = DesireRegistryDeleteView
    elif actionName == 'undelete':
        viewClass = DesireRegistryUndeleteView
    elif actionName == 'purge':
        viewClass = DesireRegisryPurgeView
    else:
        raise Exception("No view class for actionName '%s'." % actionName)
    view = viewClass(
        request=request,
        registryPath=registryPath,
        actionName=actionName,
        actionValue=actionValue
    )
    return view.getResponse()

