from dm.dom.plugin import Plugin
from dm.dom.stateful import HasManyPages 
from dm.ioc import RequiredFeature

def getProjects():
    domainRegistry = RequiredFeature('DomainRegistry')
    return domainRegistry.projects

class Plugin(Plugin):
    "Registered Plugin."

    services = HasManyPages('Service', 'name', 'project', pageKeys=getProjects)

