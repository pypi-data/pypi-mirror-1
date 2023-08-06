import pkg_resources

import dm.plugin.factory

# TODO: appears that this is only used from dom.plugin.Plugin.getSystem()
# so could replace there and get rid of this altogether ...
# (in dm also used from dm.command.plugin but that is not used I think ...)

# Todo: Make this a KForge error.
class MissingPluginEntryPoint(Exception): pass

class PluginFactory(dm.plugin.factory.PluginFactory):

    def getPluginClass(self, name):
        pluginClass = super(PluginFactory, self).getPluginClass(name)
        if not pluginClass:
            try:
                entrypoint = self.getEntryPoint(name)
            except MissingPluginEntryPoint, inst:
                msg = "Could not find plugin class either in plugin directory"
                msg += " or in otherwise defined location within a setuptools"
                msg += " entry point: %s" % str(inst)
                raise Excpetion, msg
            pluginClass = entrypoint.load()
        return pluginClass

    def getEntryPoint(self, name):
        for entrypoint in pkg_resources.iter_entry_points('kforge.plugins'):
            if entrypoint.name == name:
                return entrypoint
        msg = 'No entry point found for plugin: %s' % name
        raise MissingPluginEntryPoint(msg)

    def getEntryPoints(self):
        entrypoints = []
        for en in pkg_resources.iter_entry_points('kforge.plugins'):
            entrypoints.append(en)
        return entrypoints
