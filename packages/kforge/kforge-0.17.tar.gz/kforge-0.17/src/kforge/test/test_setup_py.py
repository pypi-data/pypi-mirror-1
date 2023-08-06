import os
import shutil

class TestSetup:
    disable = True

    def setup_class(self):
        self.dest = os.path.abspath('./src/kforge.egg-info')
        if os.path.exists(self.dest):
            shutil.rmtree(self.dest)
        cmd = 'python setup.py egg_info'
        os.system(cmd)

    def test_SOURCES(self):
        fp = os.path.join(self.dest, 'SOURCES.txt')
        contents = file(fp).read()
        exp_in = [
                'kforge/etc/kforge.conf.new',
                'bin/kforge-admin\n',
                'kforge/htdocs/project/index.html',
                ]
        exp_not_in = [
                'bin/.svn\n',
                '.svn',
                'etc/kforge.conf\n',
            ]
        for item in exp_in:
            assert item in contents
        for item in exp_not_in:
            assert item not in contents

    def test_plugins(self):
        import pkg_resources
        out = []
        for entrypoint in pkg_resources.iter_entry_points('kforge.plugins'):
            # do not actually load as that requires kforge infrastructure 
            # plugin_class = entrypoint.load()
            out.append(entrypoint.name)
        print out
        assert 'svn' in out

