import kforge.plugin.base
import kforge.utils.mailer

class Plugin(kforge.plugin.base.NonServicePlugin):
    "Notify Plugin"
    
    def __init__(self, domainObject):
        """
        Initialise plugin.

        By default an email listener will be created and registered.
        """
        super(Plugin, self).__init__(domainObject)
        self.listeners = []
        self.registerListener(self.emailNotify)

    def emailNotify(self, msg, usersToNotify):
        systemName = self.dictionary['service_name']
        domainName = self.dictionary['domain_name']
        subject = 'Changes to %s' % systemName
        fromAddress = 'kforge-noreply@' + domainName
        to = []
        for username in usersToNotify:
            email = self.registry.persons[username].email
            to.append(email)
        logmsg = 'Notify Plugin: emailNotify: sending email to %s' % to
        self.log(logmsg)
        kforge.utils.mailer.send(
                from_address=fromAddress,
                to_addresses=to, 
                subject=subject,
                body=msg)

    def registerListener(self, listener):
        """
        Register listener to listen for events.
        """
        self.listeners.append(listener)

    def notifyListeners(self, msg, usersToBeNotified = ['admin']):
        for listener in self.listeners:
            listener(msg, usersToBeNotified)
    
    def _getProjectAdmins(self, project):
        out = []
        roleAdmin = self.registry.roles['Administrator']
        for member in project.members:
            if member.role == roleAdmin:
                out.append(member.person.name)
        return out
    
    def _getSystemAdmins(self):
        # might want to put this in init for efficiency
        # (and assume that system admins do not change much over time)
        out = []
        roleAdmin = self.registry.roles['Administrator']
        for person in self.registry.persons:
            if person.role == roleAdmin:
                out.append(person.name)
        return out

    def onProjectCreate(self, project):
        msg = 'Project created: %s' % project.name
        admins = self._getProjectAdmins(project)
        sysadmins = self._getSystemAdmins()
        self.notifyListeners(msg, admins)
        self.notifyListeners(msg, sysadmins)

    def onProjectDelete(self, project):
        msg = 'Project deleted: %s' % project.name
        admins = self._getProjectAdmins(project)
        sysadmins = self._getSystemAdmins()
        self.notifyListeners(msg, admins)
        self.notifyListeners(msg, sysadmins)
       
    def onPersonCreate(self, person):
        msg = 'Person created: %s' % person.name
        sysadmins = self._getSystemAdmins()
        self.notifyListeners(msg, sysadmins)

