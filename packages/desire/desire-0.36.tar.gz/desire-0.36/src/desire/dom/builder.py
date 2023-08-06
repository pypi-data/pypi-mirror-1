import dm.dom.builder
from dm.dom.stateful import *

class ModelBuilder(dm.dom.builder.ModelBuilder):

    def construct(self):
        super(ModelBuilder, self).construct()

        self.registry.registerDomainClass(Collection)
        self.registry.collections = Collection.createRegister()

        self.registry.registerDomainClass(CollectionMembership)
        self.registry.registerDomainClass(CollectionProduct)

        self.registry.registerDomainClass(Process)
        self.registry.processes = Process.createRegister()

        self.registry.registerDomainClass(ProcessLink)

        self.registry.registerDomainClass(ProcessGoal)

        self.registry.registerDomainClass(Goal)
        self.registry.goals = Goal.createRegister()

        self.registry.registerDomainClass(ProcessEvent)

        self.registry.registerDomainClass(Event)
        self.registry.events = Event.createRegister()

        self.registry.registerDomainClass(EventStory)
        self.registry.registerDomainClass(StoryEvent)

        self.registry.registerDomainClass(Story)
        self.registry.stories = Story.createRegister()
        
        self.registry.registerDomainClass(Actor)
        self.registry.actors = Actor.createRegister()

        self.registry.registerDomainClass(ActorStory)

        self.registry.registerDomainClass(StoryRequirement)
        self.registry.registerDomainClass(RequirementLink)

        self.registry.registerDomainClass(Requirement)
        self.registry.requirements = Requirement.createRegister()

        self.registry.registerDomainClass(RequirementType)
        self.registry.requirementTypes = RequirementType.createRegister()

        self.registry.registerDomainClass(Product)
        self.registry.products = Product.createRegister()
        
        self.registry.registerDomainClass(ProductStory)

        self.registry.registerDomainClass(Walk)
        self.registry.walks = Walk.createRegister()


class SimpleDesireObject(DatedStatefulObject):

    pass


class StandardDesireObject(SimpleDesireObject):

    isUnique = False
    description = String()
    startsWithAttributeName = 'description'
    searchAttributeNames = ['description']

    def getLabelValue(self):
        return self.description or self.id


class Collection(StandardDesireObject):
    
    processes = AggregatesMany('CollectionMembership', 'process')
    products = AggregatesMany('CollectionProduct', 'product')


# todo: Rename to CollectionProcess
class CollectionMembership(SimpleDesireObject):

    collection = HasA('Collection')
    process = HasA('Process')


class CollectionProduct(SimpleDesireObject):

    collection = HasA('Collection')
    product = HasA('Product')


class Process(StandardDesireObject):
    
    collections = AggregatesMany('CollectionMembership', 'collection')
    goals = AggregatesMany('ProcessGoal', 'goal')
    events = AggregatesMany('ProcessEvent', 'event')
    links = AggregatesMany('ProcessLink', 'target', 'source')
    backLinks = AggregatesMany('ProcessLink', 'source', 'target')

    def listProducts(self):
        products = []
        for event in self.events.keys():
            for story in event.responses.keys():
                for product in story.products.keys():
                    if not product in products:
                        products.append(product)
        return products


class ProcessLink(StandardDesireObject):
    
    source = HasA('Process')
    target = HasA('Process')


class ProcessGoal(SimpleDesireObject):

    process = HasA('Process')
    goal = HasA('Goal')


class Goal(StandardDesireObject):
    
    processes = AggregatesMany('ProcessGoal', 'process')


class ProcessEvent(SimpleDesireObject):

    process = HasA('Process')
    event = HasA('Event')


class Event(StandardDesireObject):

    processes = AggregatesMany('ProcessEvent', 'process')
    responses = AggregatesMany('EventStory', 'story')
    causes = AggregatesMany('StoryEvent', 'story')


class EventStory(SimpleDesireObject):

    event = HasA('Event')
    story = HasA('Story')

    def getLabelValue(self):
        return "%s inspires %s" % (
            self.event.description,
            self.story.description,
        )

class StoryEvent(SimpleDesireObject):

    story = HasA('Story')
    event = HasA('Event')

    def getLabelValue(self):
        return "%s causes %s" % (
            self.story.description,
            self.event.description,
        )

class Story(StandardDesireObject):
    
    narrative = MarkdownText(isRequired=False)
    handles = AggregatesMany('EventStory', 'event')
    raises = AggregatesMany('StoryEvent', 'event')
    requirements = AggregatesMany('StoryRequirement', 'requirement')
    actors = AggregatesMany('ActorStory', 'actor')
    products = AggregatesMany('ProductStory', 'product')
    ticketUrl = String(isRequired=False)

    searchAttributeNames = ['description', 'narrative']


class Actor(StandardDesireObject):

    stories = AggregatesMany('ActorStory', 'story')


class ActorStory(SimpleDesireObject):

    actor = HasA('Actor')
    story = HasA('Story')


class StoryRequirement(SimpleDesireObject):

    story = HasA('Story')
    requirement = HasA('Requirement')


class RequirementLink(SimpleDesireObject):

    requirement = HasA('Requirement')
    back = HasA('Requirement')


class Requirement(StandardDesireObject):

    stories = AggregatesMany('StoryRequirement', 'story')
    type = HasA('RequirementType', default='Functional', isRequired=False)
    rationale = Text(isRequired=False)
    source = Text(isRequired=False)
    fitCriterion = Text(isRequired=False)
    satisfaction = Integer(isRequired=False)
    dissatisfaction = Integer(isRequired=False)
    dependencies = AggregatesMany('RequirementLink', 'requirement', 'back')
    conflicts = AggregatesMany('RequirementLink', 'requirement', 'back')
    supportingMaterials = Text(isRequired=False)
    history = Text(isRequired=False)
    ticketUrl = String(isRequired=False)


class RequirementType(SimpleNamedObject):

    pass


class Product(StandardDesireObject):

    collections = AggregatesMany('CollectionProduct', 'collection')
    purpose = MarkdownText(isRequired=False)
    stakeholders = MarkdownText(isRequired=False)
    users = MarkdownText(isRequired=False)
    constraints = MarkdownText(isRequired=False)
    stories = AggregatesMany('ProductStory', 'story')
    glossary = MarkdownText(isRequired=False)
    domainModel = MarkdownText(isRequired=False)
    notes = MarkdownText(isRequired=False)
    newTicketUrl = String(isRequired=False)

    def listGoals(self):
        goals = []
        for event in self.listEvents():
            for process in event.processes.keys():
                for goal in process.goals.keys():
                    if not goal in goals:
                        goals.append(goal)
        return goals

    def listEvents(self):
        events = []
        for story in self.stories.keys():
            for event in story.handles.keys():
                if not event in events:
                    events.append(event)
        return events

    def listRequirements(self):
        requirements = []
        for story in self.stories.keys():
            for requirement in story.requirements.keys():
                if not requirement in requirements:
                    requirements.append(requirement)
        return requirements

    def dictRequirementsByType(self):
        requirementsByType = {}
        for story in self.stories.keys():
            for requirement in story.requirements.keys():
                if not requirement.type in requirementsByType:
                    requirementsByType[requirement.type] = []
                requirements = requirementsByType[requirement.type]
                if not requirement in requirements:
                    requirements.append(requirement)
        return requirementsByType


class ProductStory(SimpleDesireObject):

    product = HasA('Product')
    story = HasA('Story')


class Walk(SimpleDesireObject):

    depart = HasA('Story')
    arrive = HasA('Story')



