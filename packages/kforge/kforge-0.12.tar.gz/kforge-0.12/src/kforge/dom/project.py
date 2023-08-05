from dm.dom.stateful import *

def getPlugins():
    return DomainRegistry().plugins

class Project(StandardObject):
    "Registered project."

    searchAttributeNames = ['name', 'title']

    title       = String(default='')
    description = String(default='')
    licenses    = HasMany('ProjectLicense', 'license')
    members     = HasMany('Member', 'person')
    services    = HasMany('Service', 'name')

    def delete(self):
        for member in self.members.all:
            member.delete()
        for service in self.services.all:
            service.delete()
        super(Project, self).delete()

    def undelete(self):
        super(Project, self).undelete()
        for member in self.members.all:
            member.undelete()
        for service in self.services.all:
            service.undelete()

    def purge(self):
        for license in self.licenses:
            license.delete()
        for service in self.services.all:
            service.delete()
            service.purge()
        for member in self.members.all:
            member.delete()
            member.purge()
        super(Project, self).purge()

