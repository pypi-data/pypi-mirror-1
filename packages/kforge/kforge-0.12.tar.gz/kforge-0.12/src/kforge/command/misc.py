import dm.command
import dm.command.person

import kforge.utils.mailer
import kforge.utils.password

class EmailNewPassword(dm.command.Command):
        
    def __init__(self, personName):
        super(EmailNewPassword, self).__init__()
        self.personName = personName
        self.person = None

    def loadPerson(self):
        command = dm.command.person.PersonRead(self.personName)
        command.execute()
        self.person = command.person

    def execute(self):
        super(EmailNewPassword, self).execute()
        self.loadPerson()
        newPassword = kforge.utils.password.generate()
        self.person.setPassword(newPassword)
        self.person.save()
        self._sendEmail(self.person.email, newPassword)

    def _sendEmail(self, email, newPassword):
        domainName = self.dictionary['domain_name']
        systemName = self.dictionary['system_name']
        fromAddress = 'kforge-noreply@%s' % domainName
        subject = '[%s]: Your new password' % systemName
        msg = \
'''Your new password is: %s

It is strongly recommended that you update your password when you next login.

Regards,

The %s Team
''' % (newPassword, systemName)
        kforge.utils.mailer.send(
                from_address=fromAddress,
                to_addresses=[email],
                subject=subject,
                body=msg)
