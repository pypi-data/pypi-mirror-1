from dm.dom.stateful import *

class Group(DatedStatefulObject):

    abbreviation = String(default='', isRequired=False)
    title = String(default='', isRequired=False)
    description = String(default='', isRequired=False)
    principals = AggregatesMany('GroupPrincipalship', 'researcher',
        isRequired=False)
    researchers = AggregatesMany('GroupMembership', 'researcher')
    funding = HasA('FundingStatus', isRequired=False, isSimpleOption=True)
    organisations = AggregatesMany('OrganisationGroup', 'organisation')
    external = Boolean(default=False)
    notes = Text(isRequired=False)
    # isResearchGroup = Boolean(default=True)  -- or 'type'?

    searchAttributeNames = ['title', 'description']
    startsWithAttributeName = 'title'
    
    def getLabelValue(self):
        return self.abbreviation or self.title


class GroupMembership(DatedStatefulObject):

    group = HasA('Group')
    researcher = HasA('Researcher')
    
    def getLabelValue(self):
        return "%s-%s" % (
            self.researcher.realname,
            self.group.title
        )


class GroupPrincipalship(DatedStatefulObject):

    group = HasA('Group')
    researcher = HasA('Researcher')
    
    def getLabelValue(self):
        return "%s-%s" % (
            self.researcher.realname,
            self.group.title
        )

