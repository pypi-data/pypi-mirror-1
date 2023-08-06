from dm.dom.stateful import *

class Organisation(DatedStatefulObject):

    formalName = String()
    nickname = String(isRequired=False)
    streetAddress = Text(isRequired=False)
    mainContact = Text(isRequired=False)
    billingContact = Text(isRequired=False)
    email = String(isRequired=False)
    telephone = String(isRequired=False)
    fax = String(isRequired=False)
    reference = String(isRequired=False)
    groups = HasMany('OrganisationGroup', 'group')
    accounts = HasMany('OrganisationAccount', 'account')
    notes = Text(isRequired=False)

    startsWithAttributeName = 'formalName'
    searchAttributeNames = [
        'formalName', 'nickname', 'streetAddress', 'mainContact',
        'billingContact', 'email', 'telephone', 'fax', 'reference', 'notes'
    ]

    def getLabelValue(self):
        return self.nickname or self.formalName or self.id


class OrganisationGroup(DatedStatefulObject):

    organisation = HasA('Organisation')
    group = HasA('Group')


class OrganisationAccount(DatedStatefulObject):

    organisation = HasA('Organisation')
    account = HasA('Account')

