import dm.plugin.base

class Plugin(dm.plugin.base.PluginBase):
    
    def onPersonUpdate(self, person):
        if person.researcher:
            researcher = person.researcher
            isChanged = False
            if researcher.realname != person.fullname:
                researcher.realname = person.fullname
                isChanged = True
            if researcher.email != person.email:
                researcher.email = person.email
                isChanged = True
            if isChanged:
                researcher.save()

    def onResearcherUpdate(self, researcher):
        persons = self.registry.persons.findDomainObjects(
            researcher=researcher
        )
        for person in persons:
            isChanged = False
            if person.fullname != researcher.realname:
                person.fullname = researcher.realname
                isChanged = True
            if person.email != researcher.email:
                person.email = researcher.email
                isChanged = True
            if isChanged:
                person.save()

