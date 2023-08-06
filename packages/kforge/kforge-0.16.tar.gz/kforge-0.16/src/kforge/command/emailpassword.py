import dm.command
import dm.command.person

import kforge.utils.mailer
import kforge.utils.password
from kforge.dictionarywords import SYSTEM_NAME
from kforge.dictionarywords import DOMAIN_NAME

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
        self.sendPasswordEmail(self.person.email, newPassword)

    def sendPasswordEmail(self, messageTo, newPassword):
        domainName = self.dictionary[DOMAIN_NAME]
        systemName = self.dictionary[SYSTEM_NAME]
        # todo: Put email address in the system dictionary, make configurable.
        messageFrom = 'kforge-noreply@%s' % domainName
        messageSubject = '[%s]: Your new password' % systemName
        messageBody = \
'''Your new password is: %s

It is strongly recommended that you update your password when you next login.

Regards,

The %s Team
''' % (newPassword, systemName)
        self.dispatchEmailMessage(
            messageFrom,
            messageTo,
            messageSubject,
            messageBody
        )

    # todo: Rework email dispatching. We just need one good boundary object.
    def dispatchEmailMessage(self, msgFrom, msgTo, msgSubject, msgBody):
        kforge.utils.mailer.send(
                from_address=msgFrom,
                to_addresses=[msgTo],
                subject=msgSubject,
                body=msgBody
        )

