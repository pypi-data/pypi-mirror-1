import scanbooker.testunit

class TestCase(scanbooker.testunit.TestCase):
    "Base class for View TestCases."
    
    def buildRequest(self):
        return None

