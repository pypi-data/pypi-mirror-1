from xml.dom import minidom, pulldom
import shutil
import logging
import os
import zc.recipe.egg

class PyDev(object):
    def __init__(self, buildout, name, options):
        self.buildout, self.name, self.options = buildout, name, options
        wd = self.buildout['buildout']['directory']

        self._fpath = self.options.get('pydevproject_path',
                                       os.path.join(wd, '.pydevproject'))
        self._backup_path = self.options.get('pydevproject_path',
                                       os.path.join(wd, '.pydevproject.bak'))
        self._python = options.get('target_python', 'python2.4')
        self._extra_paths = options.get('extra_paths', '').split('\n')
        self._app_eggs = filter(None, options['eggs'].split('\n'))

    def install(self):
        egg = zc.recipe.egg.Egg(self.buildout, self.name, self.options)
        egg_names, ws = egg.working_set(self._app_eggs)
        egg_paths = ws.entries + self._extra_paths
        egg_paths = [p for p in egg_paths if p.strip() != '']   #strip empty paths

        document = minidom.parse(self._fpath)

        nodes = document.getElementsByTagName('pydev_pathproperty')
        prop_node = filter(lambda node: (node.getAttribute('name') ==
                            'org.python.pydev.PROJECT_EXTERNAL_SOURCE_PATH'),
                       nodes
                   )[0]

        for child in prop_node.childNodes:
            prop_node.removeChild(child)

        for p in egg_paths:
            node = document.createElement('path')
            node.appendChild(document.createTextNode(p))
            prop_node.appendChild(node)
        shutil.copy(self._fpath, self._backup_path) #make a copy of the file
        open(self._fpath, 'w').write(document.toprettyxml())
        return self._fpath

    update = install

template = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<?eclipse-pydev version="1.0"?>
<pydev_project>
<pydev_pathproperty name="org.python.pydev.PROJECT_EXTERNAL_SOURCE_PATH">
%(paths)s
</pydev_pathproperty>
<pydev_pathproperty name="org.python.pydev.PROJECT_SOURCE_PATH">
%(src_path)s
</pydev_pathproperty>
<pydev_property name="org.python.pydev.PYTHON_PROJECT_VERSION">%(target_python)s</pydev_property>
</pydev_project>
"""
