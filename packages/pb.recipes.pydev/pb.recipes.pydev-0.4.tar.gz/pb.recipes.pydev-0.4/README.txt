A recipe that writes a .pydevproject file in a specified location. This file will
contain paths of all the eggs of the current zope instance + any other paths 
specified in the buildout.cfg file. After running the buildout you'll have to 
close and reopen the Eclipse project, to regenerate the project's module indexes. 