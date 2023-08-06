from dm.command.initialise import InitialiseDomainModel

class InitialiseDomainModel(InitialiseDomainModel):
    """
    Creates default domain model objects.
    """
    
    def __init__(self):
        super(InitialiseDomainModel, self).__init__()
 
    def execute(self):
        super(InitialiseDomainModel, self).execute()
        self.createRequirementTypes()
        self.commitSuccess()

    def createProtectionObjects(self):
        super(InitialiseDomainModel, self).createProtectionObjects()
        self.registry.protectionObjects.create('Walk')
        self.registry.protectionObjects.create('Collection')
        self.registry.protectionObjects.create('Goal')
        self.registry.protectionObjects.create('Process')
        self.registry.protectionObjects.create('Event')
        self.registry.protectionObjects.create('Story')
        self.registry.protectionObjects.create('Requirement')
        self.registry.protectionObjects.create('Product')

    def createRequirementTypes(self):
        self.registry.requirementTypes.create('Functional')
        self.registry.requirementTypes.create('Look and Feel')
        self.registry.requirementTypes.create('Usability')
        self.registry.requirementTypes.create('Performance')
        self.registry.requirementTypes.create('Operational')
        self.registry.requirementTypes.create('Maintainability and Portability')
        self.registry.requirementTypes.create('Security')
        self.registry.requirementTypes.create('Cultural and Political')
        self.registry.requirementTypes.create('Legal')

