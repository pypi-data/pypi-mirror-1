import pkg_resources

import dm.plugin.factory

# TODO: appears that this is only used from dom.plugin.Plugin.getSystem()
# so could replace there and get rid of this altogether ...
# (in dm also used from dm.command.plugin but that is not used I think ...)

class PluginFactory(dm.plugin.factory.PluginFactory):

    def getPlugin(self, domainObject):
        pluginName = domainObject.name
        pluginClass = self.getPluginClass(pluginName)
        return pluginClass(domainObject)

    def getPluginClass(self, name):
        entrypoint = self.getEntryPoint(name)
        pluginClass = entrypoint.load()
        return pluginClass

    def getEntryPoint(self, name):
        for entrypoint in pkg_resources.iter_entry_points('kforge.plugins'):
            if entrypoint.name == name:
                return entrypoint
        msg = 'No plugin entry point found for plugin: %s' % name
        raise Exception(msg)

    def getEntryPoints(self):
        entrypoints = []
        for en in pkg_resources.iter_entry_points('kforge.plugins'):
            entrypoints.append(en)
        return entrypoints
