from dm.dom.stateful import *
import dm.dom.person

class Person(dm.dom.person.Person):

    isUnique = False

    email = String(default='', isRequired=False)
    researcher = HasA('Researcher', isRequired=False)
    requestedRole = HasA('Role', isRequired=False)
    requestedGroup = HasA('Group', isRequired=False)

