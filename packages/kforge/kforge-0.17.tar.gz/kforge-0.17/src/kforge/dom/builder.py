import dm.dom.builder

class ModelBuilder(dm.dom.builder.ModelBuilder):

    def construct(self):
        super(ModelBuilder, self).construct()
        self.loadProject()
        self.loadLicense()
        self.loadService()
        self.loadMember()
        self.loadFeedEntry()

    def loadPlugin(self):  # Replace dm.dom.plugin.Plugin.
        from kforge.dom.plugin import Plugin
        self.registry.registerDomainClass(Plugin)
        self.registry.plugins = Plugin.createRegister()
        Plugin.principalRegister = self.registry.plugins

    def loadPerson(self):  # Replace dm.dom.person.Person.
        from kforge.dom.person import Person
        self.registry.registerDomainClass(Person)
        self.registry.persons = Person.createRegister()
        Person.principalRegister = self.registry.persons

    def loadProject(self):
        from kforge.dom.project import Project 
        self.registry.registerDomainClass(Project)
        self.registry.projects = Project.createRegister()
        Project.principalRegister = self.registry.projects

    def loadLicense(self):
        from kforge.dom.license import License  
        self.registry.registerDomainClass(License)
        from kforge.dom.license import ProjectLicense  
        self.registry.registerDomainClass(ProjectLicense)
        self.registry.licenses = License.createRegister()
        License.principalRegister = self.registry.licenses
        self.registry.loadBackgroundRegister(self.registry.licenses)

    def loadService(self):
        from kforge.dom.service import Service
        self.registry.registerDomainClass(Service)
        self.registry.services = Service.createRegister()
        Service.principalRegister = self.registry.services

    def loadMember(self):
        from kforge.dom.member import Member
        self.registry.registerDomainClass(Member)
        self.registry.members = Member.createRegister()
        Member.principalRegister = self.registry.members

    def loadFeedEntry(self):
        from kforge.dom.feedentry import FeedEntry
        self.registry.registerDomainClass(FeedEntry)
        self.registry.feedentries = FeedEntry.createRegister()
        FeedEntry.principalRegister = self.registry.feedentries

    def loadImage(self): # Replace dm.dom stuff -- kforge does not need Image
        pass

