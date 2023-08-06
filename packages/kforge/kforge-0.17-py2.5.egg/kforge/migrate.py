from dm.migrate import FilesDumper
from kforge.command.backup import BackupPathBuilder
import os
import shutil

class FilesDumper(FilesDumper):

    def dumpInDir(self, fileDumpDirPath):
        super(FilesDumper, self).dumpInDir(fileDumpDirPath)
        self.backupPathBuilder = BackupPathBuilder(fileDumpDirPath)
        self.dumpProjects()

    def dumpProjects(self):
        for project in self.registry.projects:
            self.dumpProjectFiles(project)

    def dumpProjectFiles(self, project):
        projectBackupPath = self.backupPathBuilder.getProjectPath(project)
        if os.path.exists(projectBackupPath):
            shutil.rmtree(projectBackupPath)
        os.makedirs(projectBackupPath)
        print "Dumping project: %s" % projectBackupPath 
        for service in project.services:
            projectPluginPath = self.backupPathBuilder.getProjectPluginPath(
                service
            )
            if not os.path.exists(projectPluginPath):
                os.makedirs(projectPluginPath)
            pluginSystem = service.plugin.getSystem()
            pluginSystem.backup(service, self.backupPathBuilder)


