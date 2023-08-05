"""
Upgrade a system service database and filesystem from one version to another.

"""
import os
import kforge.utils.db

class UpgradeDataTo0Point11(object):
    """Back up old system service configuration file and install new.
    """
    
    def execute(self):
        print \
'''To upgrade your data all you need to do is upgrade your configuration file

    1. Backup existing file (</path/to/installed/service>/etc/kforge.conf)

    2. Copy over new file (./etc/kforge.conf.new) and amend to reflect your
       new setup (suggest using your backed up configuration file).
'''

class UpgradeDbTo0Point11(kforge.utils.db.Database):
    """Upgrade system service database from 0.10 to 0.11.
    """
    
    sql = """ALTER TABLE project DROP COLUMN purpose;
            ALTER TABLE plugin ADD COLUMN state_id integer;
            ALTER TABLE plugin ADD CONSTRAINT state_id_exists FOREIGN KEY (state_id) REFERENCES state(id);
            ALTER TABLE plugin ADD COLUMN date_created timestamp without time zone;
            UPDATE plugin SET state_id = 1;
            UPDATE plugin SET date_created = now();
            """

class UpgradeDbTo0Point10(object):
    """Upgrade system service database from 0.9 to 0.10.
    
    NB: Some import statements are inline since they automatically create a
    connection to the db and we can't do this until the sql has been rewritten
    """

    def __init__(self):
        import kforge.dictionary
        sysdict = kforge.dictionary.SystemDictionary()
        self.dbuser = sysdict['db.user']
        self.dbname = sysdict['db.name']
        self.dbhost = sysdict['db.host']

    def pgsqlCommand(self, dbcmd, extra=''):
        print "Command %s requires '%s' user authentication:" % (dbcmd, self.dbuser)
        cmd = "%s -h %s -U %s %s %s" % (dbcmd, self.dbhost, self.dbuser, self.dbname, extra)
        if os.system(cmd):
            raise "ERROR (Kforge): Could not execute command: %s" % cmd
    
    def execute(self):
        self.alterRawSql()
        import kforge.dom
        self.registry = kforge.dom.DomainRegistry()
        self.createAccessControlData()
        self.createPersonalGrants()
        self.createPlugins()
    
    def alterRawSql(self):
        sql = """DROP TABLE role_permission;
    DROP TABLE permission;
    DROP TABLE protection_object;
    DROP TABLE permission_type;
    
    ALTER TABLE person ADD COLUMN role_id integer;
    ALTER TABLE person ADD CONSTRAINT role_id_exists FOREIGN KEY (role_id) REFERENCES role (id);
    
    UPDATE role SET name = 'Visitor' where name = 'Guest';
    DELETE FROM member where role_id = 5 or role_id = 6;
    DELETE FROM role where name = 'SystemAdministrator' OR name = 'SystemGuest';
    -- # get rid of sysadmin role and system guest role
    UPDATE person SET name = 'visitor' where name = 'guest';
    -- make all people have general role visitor
    UPDATE person SET role_id = 4;
    -- make 
    UPDATE person SET role_id = 1 where name = 'admin';"""
        self.pgsqlCommand('psql', '-c "%s"' % sql)
    
    def createAccessControlData(self):
        import kforge.command.initialise
        roles = self.registry.roles
        initialiseCmd = kforge.command.initialise.InitialiseDomainModel()
        initialiseCmd.adminRole = roles['Administrator']
        initialiseCmd.developerRole = roles['Developer']
        initialiseCmd.friendRole    = roles['Friend']
        initialiseCmd.visitorRole   = roles['Visitor']
        initialiseCmd.createSystem()
        initialiseCmd.createActions()
        initialiseCmd.createProtectionObjects()
        initialiseCmd.createGrants()
        initialiseCmd.createRefusals()
        initialiseCmd.createPersonalBars()
        
    def createPersonalGrants(self):
        protectionClass = self.registry.getDomainClass('ProtectionObject')
        for person in self.registry.persons:
            protectedName = protectionClass.makeProtectedName(person)
            protectionObject = self.registry.protectionObjects.create(protectedName)
            for permission in protectionObject.permissions:
                if not permission in person.grants:
                    person.grants.create(permission)
    
    def createPluginPermissions(self):
        for plugin in self.registry.plugins:
            plugin.getSystem().onCreate()
    
    def createPlugins(self):
        self.registry.plugins.create('accesscontrol')

