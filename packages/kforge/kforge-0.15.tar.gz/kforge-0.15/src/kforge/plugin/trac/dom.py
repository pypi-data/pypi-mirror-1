from dm.dom.stateful import *
from kforge.ioc import *

registry = RequiredFeature('DomainRegistry')
    
def getSvnChoices(tracProject):
    if not tracProject:
        return []
    svnPlugin = registry.plugins['svn']
    projectSvnRegister = svnPlugin.services[tracProject.service.project]
    return [(s.id, s.name) for s in projectSvnRegister]
        
class TracProject(SimpleObject):
    "Definition of TracProject domain object."

    isEnvironmentInitialised = Boolean(isHidden=True)
    service = HasA('Service', comment='A trac service.')
    svn     = HasA('Service', getChoices=getSvnChoices, title='Subversion repository', comment='A project subversion service.', isRequired=False)
    path    = String(isHidden=True, default='/', title='Svn path', isRequired=False, comment='A path within the chosen Subversion repository.')

    def getLabelValue(self):
        svnLabelValue = ''
        if self.svn:
            svnLabelValue = self.svn.getLabelValue()
        else:
            svnLabelValue = 'no-subversion-repository'
        if self.service:
            serviceLabelValue = self.service.getLabelValue()
        else:
            serviceLabelValue = 'no-parent-service'
        
        return "%s-%s" % (
            serviceLabelValue,
            svnLabelValue,
        )
            

registry.registerDomainClass(TracProject)

