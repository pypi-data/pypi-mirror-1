from dm.accesscontrol import SystemAccessController
from dm.exceptions import *
from scanbooker.dictionarywords import AC_SKIP_ROLE_INFERENCE

moddebug = False

class AccessController(SystemAccessController):
    "Introduces project member role to access controller."

    def assertAccessNotAuthorised(self):
        self.assertInferredRoleNotAuthorised()
        super(AccessController, self).assertAccessNotAuthorised()

    def assertInferredRoleNotAuthorised(self):
        if self.dictionary[AC_SKIP_ROLE_INFERENCE]:
            return
        roleName = self.inferRoleName()
        if roleName:
            role = self.registry.roles[roleName]
            msg = "inferred %s role" % role.name.lower()
            self.assertRoleNotAuthorised(role, msg)

    def inferRole(self):
        return None

    def inferRoleName(self):
        roleName = ''
        if self.isProtectedObjectClassName('Person'):
            if self.person == self.protectedObject:
                return 'PrincipalInvestigator'
        viewingResearcher = self.person.researcher
        if not viewingResearcher:
            return ''  # E.g. user account not associated with a researcher.
        if self.isProtectedObjectClassName('Person'):
            researcher = self.protectedObject.researcher
            if not researcher:
                return ''
            groupList = []
            groupList += researcher.principalships.keys()
            groupList += researcher.memberships.keys()
            for group in groupList:
                if viewingResearcher in group.principals:
                    return 'PrincipalInvestigator'
            for group in groupList:
                if viewingResearcher in group.researchers:
                    return 'Researcher'
        elif self.isProtectedObjectClassName('Approval'):
            approval = self.protectedObject
            if viewingResearcher in approval.principalInvestigators:
                return 'PrincipalInvestigator'
            if viewingResearcher in approval.additionalResearchers:
                return 'Researcher'
        elif self.isProtectedObjectClassName('Group'):
            group = self.protectedObject
            if viewingResearcher in group.principals:
                return 'PrincipalInvestigator'
            elif viewingResearcher in group.researchers:
                return 'Researcher'
        elif self.isProtectedObjectClassName('Researcher'):
            researcher = self.protectedObject
            groupList = []
            groupList += researcher.principalships.keys()
            groupList += researcher.memberships.keys()
            for group in groupList:
                if viewingResearcher in group.principals:
                    return 'PrincipalInvestigator'
            for group in groupList:
                if viewingResearcher in group.researchers:
                    return 'Researcher'
        elif self.isProtectedObjectClassName('Project'):
            project = self.protectedObject
            if viewingResearcher == project.leader:
                return 'PrincipalInvestigator'
            if viewingResearcher in project.researchers:
                return 'Researcher'
        elif self.isProtectedObjectClassName('Report'):
            report = self.protectedObject
            # Report currently implies nothing about the role.
        return roleName
    
    def isProtectedObjectClassName(self, className):
        protectedObjectClass = self.protectedObject.__class__
        namedClass = self.registry.getDomainClass(className)
        return protectedObjectClass == namedClass
        
    def isResearcherPerson(self):
        if self.isProtectedObjectClassName('Researcher'):
            researcher = self.protectedObject
            if researcher == self.person.researcher:
                return True
        return False

