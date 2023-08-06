"""
The ScanBooker system is a *domainmodel* application, designed to support medical imaging administration.
"""

# Done: Fix reportsTo bug in access controller. Write test to uncover issue.
# Done: Fix accounts, to remove confusion between user and cost accounts.
# Done: Prepare, test, and release ScanBooker 0.20.
# Done: Upgrade demo service for version 0.20.
# Done: Fix organisations to have groups.

# Todo: Improve presentation of exceptions.
# Todo: Fix Django DEBUG setting, so only debug or development versions show error message.

# Todo: Create scanbooker-vmf script to generate virtual machine file.


__version__ = '0.23'

def getA():
    import scanbooker.soleInstance
    return scanbooker.soleInstance.application

