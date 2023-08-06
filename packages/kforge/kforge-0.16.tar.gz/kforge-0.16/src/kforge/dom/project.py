from dm.dom.stateful import *

def getPlugins():
    return DomainRegistry().plugins

class Project(StandardObject):
    "Registered project."

    searchAttributeNames = ['name', 'title', 'description']

    title       = String(default='')
    description = String(default='')
    licenses    = HasMany('ProjectLicense', 'license')
    members     = HasMany('Member', 'person')
    services    = HasMany('Service', 'name')

    isUnique = False

    def delete(self):
        for member in self.members.getAll():
            member.delete()
        for service in self.services.getAll():
            service.delete()
        super(Project, self).delete()

    def undelete(self):
        super(Project, self).undelete()
        for member in self.members.getAll():
            member.undelete()
        for service in self.services.getAll():
            service.undelete()

    def purge(self):
        for license in self.licenses:
            license.delete()
        for service in self.services.getAll():
            service.delete()
            service.purge()
        for member in self.members.getAll():
            member.delete()
            member.purge()
        super(Project, self).purge()

    def getLabelValue(self):
        return self.title or self.name

