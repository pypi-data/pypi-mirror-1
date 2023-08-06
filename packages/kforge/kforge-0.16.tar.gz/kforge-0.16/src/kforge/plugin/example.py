"""
Example plugin module.

To create a new KForge plugin:

    1. Duplicate this example.py module with the new (lowercase) plugin name.
    2. Rename the Example class after the new (CamelCase) plugin name.
    3. Edit the createPlugin() method below to use your new (CamelCase) plugin class.
    4. Implement the various on() methods appropriately.
    5. Deploy your new plugin by adding the (lowercase) plugin name to plugin.conf file.

    *  Write unittest class for the example. Also provide indications for changing this file.

"""

import kforge.plugin.base
from kforge.ioc import *

debug = RequiredFeature('Debug')

class Plugin(kforge.plugin.base.ServicePlugin):
    "Example plugin."

    def __init__(self, domainObject):
        super(Plugin, self).__init__(domainObject)
        self.counts = {}
        self.counts['onRun'] = 0
        self.counts['onProjectCreate'] = 0
        self.counts['onProjectUpdate'] = 0
        self.counts['onProjectApprove'] = 0
        self.counts['onProjectDelete'] = 0
        self.counts['onProjectUndelete'] = 0
        self.counts['onProjectPurge'] = 0
        self.counts['onPersonCreate'] = 0
        self.counts['onPersonUpdate'] = 0
        self.counts['onPersonApprove'] = 0
        self.counts['onPersonDelete'] = 0
        self.counts['onPersonUndelete'] = 0
        self.counts['onPersonPurge'] = 0
        self.counts['onMemberCreate'] = 0
        self.counts['onMemberUpdate'] = 0
        self.counts['onMemberApprove'] = 0
        self.counts['onMemberDelete'] = 0
        self.counts['onMemberUndelete'] = 0
        self.counts['onMemberPurge'] = 0
        self.counts['onServiceCreate'] = 0
        self.counts['onServiceUpdate'] = 0
        self.counts['onServiceApprove'] = 0
        self.counts['onServiceDelete'] = 0
        self.counts['onServiceUndelete'] = 0
        self.counts['onServicePurge'] = 0

    def onRun(self, sender):
        if debug:
            self.logger.debug("Example plugin received onRun event.")
        self.counts['onRun'] += 1

    def onProjectCreate(self, project):
        if debug:
            self.logger.debug("Example plugin received onProjectCreate event!")
        self.counts['onProjectCreate'] += 1

    def onProjectUpdate(self, project):
        if debug:
            self.logger.debug("Example plugin received onProjectUpdate event!")
        self.counts['onProjectUpdate'] += 1

    def onProjectApprove(self, project):
        if debug:
            self.logger.debug("Example plugin received onProjectApprove event!")
        self.counts['onProjectApprove'] += 1

    def onProjectDelete(self, project):
        if debug:
            self.logger.debug("Example plugin received onProjectDelete event!")
        self.counts['onProjectDelete'] += 1

    def onProjectUndelete(self, project):
        if debug:
            self.logger.debug("Example plugin received onProjectUndelete event!")
        self.counts['onProjectUndelete'] += 1

    def onProjectPurge(self, project):
        if debug:
            self.logger.debug("Example plugin received onProjectPurge event!")
        self.counts['onProjectPurge'] += 1

    def onPersonCreate(self, project):
        if debug:
            self.logger.debug("Example plugin received onPersonCreate event!")
        self.counts['onPersonCreate'] += 1 

    def onPersonUpdate(self, project):
        if debug:
            self.logger.debug("Example plugin received onPersonUpdate event!")
        self.counts['onPersonUpdate'] += 1

    def onPersonApprove(self, project):
        if debug:
            self.logger.debug("Example plugin received onPersonApprove event!")
        self.counts['onPersonApprove'] += 1

    def onPersonDelete(self, project):
        if debug:
            self.logger.debug("Example plugin received onPersonDelete event!")
        self.counts['onPersonDelete'] += 1

    def onPersonUndelete(self, project):
        if debug:
            self.logger.debug("Example plugin received onPersonUndelete event!")
        self.counts['onPersonUndelete'] += 1

    def onPersonPurge(self, project):
        if debug:
            self.logger.debug("Example plugin received onPersonPurge event!")
        self.counts['onPersonPurge'] += 1

    def onMemberCreate(self, project):
        if debug:
            self.logger.debug("Example plugin received onMemberCreate event!")
        self.counts['onMemberCreate'] += 1

    def onMemberUpdate(self, project):
        if debug:
            self.logger.debug("Example plugin received onMemberUpdate event!")
        self.counts['onMemberUpdate'] += 1

    def onMemberApprove(self, project):
        if debug:
            self.logger.debug("Example plugin received onMemberApprove event!")
        self.counts['onMemberApprove'] += 1

    def onMemberDelete(self, project):
        if debug:
            self.logger.debug("Example plugin received onMemberDelete event!")
        self.counts['onMemberDelete'] += 1
    
    def onMemberUndelete(self, project):
        if debug:
            self.logger.debug("Example plugin received onMemberUndelete event!")
        self.counts['onMemberUndelete'] += 1
    
    def onMemberPurge(self, project):
        if debug:
            self.logger.debug("Example plugin received onMemberPurge event!")
        self.counts['onMemberPurge'] += 1
    
    def onServiceUpdate(self, project):
        if debug:
            self.logger.debug("Example plugin received onServiceUpdate event!")
        self.counts['onServiceUpdate'] += 1

    def onServiceCreate(self, project):
        if debug:
            self.logger.debug("Example plugin received onServiceCreate event!")
        self.counts['onServiceCreate'] += 1

    def onServiceApprove(self, project):
        if debug:
            self.logger.debug("Example plugin received onServiceApprove event!")
        self.counts['onServiceApprove'] += 1

    def onServiceDelete(self, project):
        if debug:
            self.logger.debug("Example plugin received onServiceDelete event!")
        self.counts['onServiceDelete'] += 1
    
    def onServiceUndelete(self, project):
        if debug:
            self.logger.debug("Example plugin received onServiceUndelete event!")
        self.counts['onServiceUndelete'] += 1
    
    def onServicePurge(self, project):
        if debug:
            self.logger.debug("Example plugin received onServicePurge event!")
        self.counts['onServicePurge'] += 1
    
    def getApacheConfig(self, service):
        return """
        <Location %(urlPath)s>
            
            %(accessControl)s
        </Location>"""

    def getUserHelp(self, service):
        serviceUrl = service.getUrl()
        helpMessage = '''
<p>These are instructions on how to use this example service. The service
is available online at:<a href="%s">%s</a></p>
<p>You can just visit it by clicking on the link. Be warned though, you will not
find anything there as the example plugin does not do anything (it is just an
example of a plugin rather than a real one).</p> ''' % (serviceUrl,
        serviceUrl)
        return helpMessage


