from desire.dom.testunit import TestCase
import unittest

def suite():
    suites = [
        unittest.makeSuite(TestProcess),
        unittest.makeSuite(TestProduct),
        unittest.makeSuite(TestWalk),
        #unittest.makeSuite(TestCollection),
        #unittest.makeSuite(TestGoal),
        #unittest.makeSuite(TestEvent),
        #unittest.makeSuite(TestResponse),
        #unittest.makeSuite(TestRequirement),
    ]
    return unittest.TestSuite(suites)


class TestProcess(TestCase):

    processDescription = 'A fictional process.'

    def setUp(self):
        super(TestProcess, self).setUp()
        self.process = self.registry.processes.create(description=self.processDescription)
        self.processId = self.process.id

    def tearDown(self):
        super(TestProcess, self).tearDown()
        if self.processId in self.registry.processes:
            process = self.registry.processes[self.processId]
            process.delete()

    def test_create(self):
        self.failUnless(self.process)


class TestWalk(TestCase):

    story1Description = 'A walked story 1.'
    story2Description = 'A walked story 2.'
    story3Description = 'A walked story 3.'

    def setUp(self):
        super(TestWalk, self).setUp()
        self.walk1 = None
        self.story1 = self.registry.stories.create(description=self.story1Description)
        self.story2 = self.registry.stories.create(description=self.story2Description)
        self.story3 = self.registry.stories.create(description=self.story3Description)

    def tearDown(self):
        super(TestWalk, self).tearDown()
        if self.walk1:
            self.walk1.delete()
        self.story1.delete()
        self.story2.delete()
        self.story3.delete()

    def test_create(self):
        self.walk1 = self.registry.walks.create(
            depart=self.story1,
            arrive=self.story2,
        )
        self.failUnless(self.walk1)
        self.failUnlessEqual(self.walk1.depart, self.story1)
        self.failUnlessEqual(self.walk1.arrive, self.story2)
   

class TestProduct(TestCase):

    productDescription = 'A fictional product.'
    story1Description = 'A fictional story 1.'
    story2Description = 'A fictional story 2.'
    story3Description = 'A fictional story 3.'
    reqmt1Description = 'A fictional reqmt 1.'
    reqmt2Description = 'A fictional reqmt 2.'
    reqmt3Description = 'A fictional reqmt 3.'

    def setUp(self):
        super(TestProduct, self).setUp()
        self.product = self.registry.products.create(description=self.productDescription)
        self.story1 = self.registry.stories.create(description=self.story1Description)
        self.story2 = self.registry.stories.create(description=self.story2Description)
        self.story3 = self.registry.stories.create(description=self.story3Description)
        self.product.stories.create(self.story1)
        self.product.stories.create(self.story2)
        self.product.stories.create(self.story3)
        self.reqmt1 = self.registry.requirements.create(description=self.reqmt1Description,
            type=self.registry.requirementTypes['Functional'])
        self.reqmt2 = self.registry.requirements.create(description=self.reqmt2Description,
            type=self.registry.requirementTypes['Look and Feel'])
        self.reqmt3 = self.registry.requirements.create(description=self.reqmt3Description,
            type=self.registry.requirementTypes['Performance'])
        self.story1.requirements.create(self.reqmt1)
        self.story2.requirements.create(self.reqmt1)
        self.story2.requirements.create(self.reqmt2)
        self.story3.requirements.create(self.reqmt1)
        self.story3.requirements.create(self.reqmt2)
        self.story3.requirements.create(self.reqmt3)
        self.productId = self.product.id

    def tearDown(self):
        super(TestProduct, self).tearDown()
        if self.productId in self.registry.products:
            product = self.registry.products[self.productId]
            product.delete()
        self.story1.delete()
        self.story2.delete()
        self.story3.delete()
        self.reqmt1.delete()
        self.reqmt2.delete()
        self.reqmt3.delete()

    def test_create(self):
        self.failUnless(self.product)
   
    def test_dictRequirementsByType(self):
        reqmtsByType = self.product.dictRequirementsByType()
        self.failUnless(reqmtsByType)

