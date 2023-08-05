from xml.dom import minidom, pulldom
import shutil
import logging
import os
import zc.recipe.egg

class PyDev(object):
    def __init__(self, buildout, name, options):
        self.buildout, self.name, self.options = buildout, name, options
        wd = self.buildout['buildout']['directory']

        res = []
        develop_locations = self.buildout['buildout']['directory']
        for path in develop_locations:
            res.append(os.path.normpath(os.path.join(wd, './src')))
        self._ignored_paths = res

        self._fpath = self.options.get('pydevproject_path',
                                       os.path.join(wd, '.pydevproject'))
        self._backup_path = "%s.bak" % self._fpath
        self._python = options.get('target_python', 'python2.4')
        self._extra_paths = options.get('extra_paths', '').split('\n')
        self._app_eggs = filter(None, options['eggs'].split('\n'))

    def install(self):
        egg = zc.recipe.egg.Egg(self.buildout, self.name, self.options)
        egg_names, ws = egg.working_set(self._app_eggs)
        egg_paths = ws.entries + self._extra_paths
        egg_paths = [p for p in egg_paths if p.strip() != '']   #strip empty paths

        #strip develop paths,they're probably in Eclipse source path
        egg_paths = filter(lambda p: p not in self._ignored_paths, egg_paths)

        document = minidom.parse(self._fpath)

        nodes = document.getElementsByTagName('pydev_pathproperty')
        prop_node = filter(lambda node: (node.getAttribute('name') ==
                            'org.python.pydev.PROJECT_EXTERNAL_SOURCE_PATH'),
                       nodes
                   )[0]
        clone = prop_node.cloneNode(False)

        for p in egg_paths:
            node = document.createElement('path')
            node.appendChild(document.createTextNode(p))
            clone.appendChild(node)

        parent = prop_node.parentNode
        parent.replaceChild(clone, prop_node)

        shutil.copy(self._fpath, self._backup_path) #make a copy of the file
        open(self._fpath, 'w').write(document.toxml())
        return ""

    update = install