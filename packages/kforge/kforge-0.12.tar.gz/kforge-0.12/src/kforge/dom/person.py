from dm.dom.stateful import *
import dm.dom.person
import md5

class Person(dm.dom.person.Person):
    "Registered person."

    memberships = HasMany('Member', 'project')

    def delete(self):
        for member in self.memberships:
            member.delete()
        super(Person, self).delete()

    def purge(self):
        for member in self.memberships.all:
            member.delete()
            member.purge()
        super(Person, self).purge()

