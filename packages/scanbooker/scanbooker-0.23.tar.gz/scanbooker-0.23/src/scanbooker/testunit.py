import dm.testunit
import scanbooker.application

#class DevApplication(scanbooker.application.Application):
#    pass

class TestCase(dm.testunit.TestCase):
    "Base class for scanbooker TestCases."
    pass

class ApplicationTestSuite(dm.testunit.ApplicationTestSuite):
    pass #appBuilderClass = scanbooker.builder.ApplicationBuilder

