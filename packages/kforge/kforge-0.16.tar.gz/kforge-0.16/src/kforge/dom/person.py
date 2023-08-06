from dm.dom.stateful import *
import dm.dom.person
import md5

class Person(dm.dom.person.Person):
    "Registered person."

    memberships = HasMany('Member', 'project')

    isUnique = False

    def delete(self):
        for member in self.memberships:
            member.delete()
        super(Person, self).delete()

    def purge(self):
        for member in self.memberships.getAll():
            member.delete()
            member.purge()
        super(Person, self).purge()

    def getLabelValue(self):
        return self.fullname or self.name

    def getFirstName(self):
        name = self.getLabelValue()
        parts = name.split(' ')
        return parts[0]
