#!/usr/bin/env python
"""
This module provides classes and utilities to migrate a gforge system to kforge

Currently the following are migrated:
    1. users
    2. projects
    3. memberships
    4. licenses (where possible)
    5. roles (where possible)

See individuals classes for more details.

All internal Kforge errors, for example those arising from an attempt to create
an object that already exist in destination KForge system do not halt migration
but result in an error being logged.
"""
import time
import sqlobject

import kforge.command
import kforge.exceptions

# ==================
# CONFIGURATION DATA
gforgeDbUser = 'kforgetest'
gforgeDbPass = 'pass'
gforgeDbHost = 'localhost'
gforgeDbName = 'gforge'
# ==================

"Dictionaries to map gforge ids to kforge objects, keyed by object type"
mappers = { 'User' : {}, 'Group' : {} }

class GforgeMapper(sqlobject.SQLObject):
    """
    Base class for mapper from gforge to kforge.
    
    Provides connection to gforge database and a kforge registry
    
    """
    uri = "postgres://%s:%s@%s/%s" % (gforgeDbUser, gforgeDbPass, gforgeDbHost, gforgeDbName) 
    _connection = sqlobject.connectionForURI(uri)
   
    app = kforge.command.application
    registry = app.registry
    logger   = app.logger
    
    def migrateAll(self):
        for xyz in self.select():
            if not xyz.isExcluded():
                xyz.migrate()
    
    migrateAll = classmethod(migrateAll)
    
    def deleteAll(self):
        for key in self.mapping.keys():
            self.mapping[key].delete()
            self.mapping[key].purge()
    
    deleteAll = classmethod(deleteAll)

class License(GforgeMapper):
    """
    Does not work because licenes table does not have a primary key.
    Cannot be bothered to fix this so hack things in project for time being
    
    TODO: hand encode explicit mappings from gforge to our system
    GNU General Public License (GPL)
    
    _table = 'licenses'
    _idName = 'license_id'
    _idSequence = 'licenses_license_id_seq'
    _fromDatabase = True
    
    # have to create this even though in parent as o/w mapping does not work
    app = kforge.command.application
    registry = app.registry
    
    # exclude all of them for time being
    defaultExcludes = [ 100, # None
                        101, # GNU General Public License (GPL)
                        102, # GNU Library Public License (LGPL)
                        103, # BSD License
                        104, # MIT License
                        105, # Artistic License
                        106, # Mozilla Public License 1.0 (MPL)
                        107, # Qt Public License (QPL)
                        108, # IBM Public License
                        109, # MITRE Collaborative Virtual Workspace License (CVW License)
                        110, # Ricoh Source Code Public License
                        111, # Python License
                        112, # zlib/libpng License
                        113, # Apache Software License
                        114, # Vovida Software License 1.0
                        115, # Sun Internet Standards Source License (SISSL)
                        116, # Intel Open Source License
                        117, # Mozilla Public License 1.1 (MPL 1.1)
                        118, # Jabber Open Source License
                        119, # Nokia Open Source License
                        120, # Sleepycat License
                        121, # Nethack General Public License
                        122, # IBM Common Public License
                        123, # Apple Public Source License
                        124, # Public Domain
                        125, # Website Only
                        126, # Other/Proprietary License
                        ]
    actualExcludes = defaultExcludes
    mapping = { 
                }
    
    def isExcluded(self):
        if self.licenseName in actualExcludes: return True
        else: return False
    
    def migrate(self):
        license = self.registry.licenes.create(name=self.licenseName)
        self.mapping[self.id] = license
"""

class User(GforgeMapper):
    
    _table = 'users'
    _idName = 'user_id'
    _idSequence = 'users_pk_seq'
    _fromDatabase = True
    # hack to get rid of foreign key setting which then results in wrong col name
    ccode = sqlobject.IntCol()
    
    defaultExcludes = ['admin', 'None']
    actualExcludes = defaultExcludes + ['rpollock']
    
    mapping = mappers['User']
    
    def isExcluded(self):
        if self.userName in self.actualExcludes: return True
        else: return False
    
    def migrate(self):
        personCmd = kforge.command.PersonCreate(self.userName)
        try:
            personCmd.execute()
            person = personCmd.person
            self.mapping[self.id] = person
            
            person.email = self.email
            person.fullname = self.realname
            person.dateCreated = time.ctime(self.addDate)
            person.save()
            # hack the password to transfer across md5 hashes directly
            # Do NOT call save after this on domain object or we have problems
            person.record.password = self.userPw
        except kforge.exceptions.KforgeError,inst:
            self.logger.error(inst)

class Group(GforgeMapper):
    
    _table = 'groups'
    _idName = 'group_id'
    _idSequence = 'groups_pk_seq'
    _fromDatabase = True
    
    # hack to rename as this is a foreign key so sqlobject adds id at end
    license = sqlobject.IntCol()
    
    defaultExcludes = ['stats', 'peerrating', 'siteadmin', 'newsadmin' ]
    actualExcludes = defaultExcludes + ['test0', 'sacrifice', 'pkmanager']
    
    mapping = mappers['Group']
    
    def isExcluded(self):
        if self.unixGroupName in self.actualExcludes: return True
        else: return False
    
    def migrate(self):
        try:
            projectCmd = kforge.command.ProjectCreate(self.unixGroupName)
            projectCmd.execute()
            project = projectCmd.project
            self.mapping[self.id] = project
            project.title = self.groupName
            project.dateCreated = time.ctime(self.registerTime)
            project.purpose = self.registerPurpose
            project.description = self.shortDescription
            project.save()
            
            # now do license
            # todo get the licenses properly
            licenseMapping = {  101 : self.registry.licenses[2],
                                103 : self.registry.licenses[3]
                                }
            otherLicense = self.registry.licenses[1]
            if licenseMapping.has_key(self.license):
                project.licenses.create(licenseMapping[self.license])
            else:
                project.licenses.create(otherLicense)
        except kforge.exceptions.KforgeError, inst:
            self.logger.error(inst)


class Member(GforgeMapper):
    """
    Roles: Only migrate admin roles so normal members will simply be given the
    default project role
    """
    
    _table = 'user_group'
    _idName = 'user_group_id'
    _idSequence = 'user_group_pk_seq'
    _fromDatabase = True
    
    def isExcluded(self):
        user = User.get(self.userID)
        group = Group.get(self.groupID)
        if user.isExcluded() or group.isExcluded():
            return True
        else:
            return False
    
    def migrate(self):
        try:
            project = mappers['Group'][self.groupID]
            member = project.members.create(mappers['User'][self.userID])
            self.developerRole = self.registry.roles['Developer']
            self.adminRole = self.registry.roles['Administrator']
            
            if self.adminFlags.startswith('A'):
                member.role = self.adminRole
            else:
                member.role = self.developerRole
            member.save()
        except kforge.exceptions.KforgeError, inst:
            self.logger.error(inst)

import unittest
class MigrateTest(unittest.TestCase):
    
    app = kforge.command.application
    registry = app.registry
    
    def setUp(self):
        try:
            User.migrateAll()
            Group.migrateAll()
            Member.migrateAll()
        except:
            self.tearDown()
            raise
    
    def tearDown(self):
        User.deleteAll()
        Group.deleteAll()
    
    def testUserMigrate(self):
        for user in User.select():
            if not user.isExcluded():
                self.assertTrue(self.registry.persons.has_key(user.userName), user.userName)
                self.assertTrue(self.registry.persons[user.userName].password == user.userPw)
    
    def testGroupMigrate(self):
        for group in Group.select():
            if not group.isExcluded():
                self.assertTrue(self.registry.projects.has_key(group.unixGroupName), group.unixGroupName)
                project = self.registry.projects[group.unixGroupName]
                self.assertEquals(project.dateCreated.strftime(), time.ctime(group.registerTime))
    
    def testMemberMigrate(self):
        adminRole = self.registry.roles['Administrator']
        for group in Group.select():
            if not group.isExcluded():
                project = self.registry.projects[group.unixGroupName]
                memberships = Member.select(Member.q.groupID==group.id)
                for member in memberships:
                    user = User.get(member.userID)
                    if not user.isExcluded():
                        kforgeUser = User.mapping[member.userID]
                        self.assertTrue(project.members.has_key(kforgeUser))
                        if member.adminFlags.startswith('A'):
                            self.assertTrue(project.members[kforgeUser].role == adminRole)

def migrateGforgeToKforge():
    print 'Starting migration .....'
    startTime = time.time()
    try:
        User.migrateAll()
        Group.migrateAll()
        Member.migrateAll()
        timeElapsed = int(time.time() - startTime)
        print 'Migration: SUCCESS (time taken: %ss)' % timeElapsed
    except Exception, inst:
        print 'Migration: FAILURE'
        print 'Details: '
        print inst
        print 'Rolling back ...'
        User.deleteAll()
        Group.deleteAll()
        print 'Roll back: COMPLETE'

if __name__ == '__main__':
    import optparse
    usage  = 'usage: %prog [options]'
    parser = optparse.OptionParser(usage)
    parser.add_option('-t', '--test',
        action='store_true', dest='unittest', default=False,
        help='Run unit tests for migration')
    
    (options, args) = parser.parse_args()
    
    if options.unittest:
        unittest.TextTestRunner().run(unittest.makeSuite(MigrateTest))
    else:
        migrateGforgeToKforge()
