#!/usr/bin/env python

#    xpyenv - makes virtual python enviromnents easy 
#    Copyright (C) 2010  Emiliano Dalla Verde Marcozzi / aka: x-ip

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import sys
import urllib
import subprocess

class RootPyEnv(object):
    """ The RootPyEnv class have methods that helps build a python virtual environment.
    """

    urls = ['http://peak.telecommunity.com/dist/ez_setup.py',
            'http://peak.telecommunity.com/dist/virtual-python.py']
    
    def getPythonEnv(self):
        """ Returns a string path to the folder where the python virtual
        environments are stored
        """
        pyenv = os.getenv('HOME') + '/.pythones'
        return pyenv
    
    def pythonEnvExist(self):
        """ Check if the Python Environment directory exists. If exists, return
        True, otherwise return False
        """
        pyenv = self.getPythonEnv()
        if not os.path.exists(pyenv):
            return False
        else:
            return True
        
    def createDir(self, dir):
        """ createDir takes one argument. Simply pass to it a string and it will create the
        directory. 
        """ 
        os.makedirs(dir)
        print "Creado el directorio: %s" % dir
            
    def changeDir(self, dir):
        """ Change the location where the scripts runs. changeDir takes a string as args and change
        to that directory.
        """
        print "Cambiando al directorio: %s" % dir
        os.chdir(dir)
    
    def downloadWebFile(self, url, path):
        self.changeDir(path)
        
        print "Descargando: %s" % url
        webfile = urllib.urlopen(url)
        localfile = open(url.split('/')[-1], 'w')
        
        print "Guardando ... "
        localfile.write(webfile.read())
        
        print "Hecho! Ajustando Permisos ..."
        os.chmod(localfile.name, 0700)
        
        webfile.close()
        localfile.close()

    def getPytmp(self):
        pytmp = self.getPythonEnv() + '/pytmp'
        return pytmp
     
    def createRootPyenv(self):
        if not self.pythonEnvExist():
            destdir = self.getPythonEnv()
            self.createDir(destdir)

            for url in self.urls:
                self.downloadWebFile(url, destdir)

            pytmp = self.getPytmp() 
            vpython = destdir + '/virtual-python.py'
            ezsetup = destdir + '/ez_setup.py'
            py = pytmp + '/bin/python'
            easyinstall = pytmp + '/bin/easy_install'
            
            print "Inicializando python temporal ..."
            os.makedirs(pytmp)
            self.changeDir(pytmp)

            print "Creando python temporal ..."
            subprocess.call(["python", vpython, "--no-site-packages", "--prefix=%s" % pytmp])
            
            print "Ejecutando ez_setup.py ..."
            subprocess.call([py, ezsetup])
            
            print "Instalando VirtualEnv ..."
            subprocess.call([easyinstall, "virtualenv"])
            
            print "Borrando la evidencia :) ..."
            os.remove(vpython)
            os.remove(ezsetup)
        else:
            pass

    def getVirtualEnv(self):
        virtualenv = self.getPytmp() + '/bin/virtualenv'
        return virtualenv
        
        
class PyEnv(RootPyEnv):
    
    def doitrightnow(self, version):
        print "Chequeando el Root Virtual Python... "
        self.createRootPyenv()
        pyenv_path = self.getPythonEnv() + '/' + version
        
        if not os.path.exists(pyenv_path):
            print "Creando el directorio: %s" % pyenv_path
            os.makedirs(pyenv_path)
            
        ve = self.getVirtualEnv()
        version = "--python=%s" % version
        subprocess.call([ve, version, pyenv_path])
        
        alias = 'alias py2' + version.split('.')[-1] + '="source ' +    \
                                            pyenv_path + '/bin/activate"'
        self.addAliasToBashrc(alias)
        print "Puedes usar tu nuevo python virtual, simplemente abriendo un nuevo shell y escribiendo:"
        print "\nbash$: py2%s" % version.split('.')[-1]
        
    def addAliasToBashrc(self, alias):
        bashrc = os.getenv('HOME') + '/.bashrc'
        result = [(line_number+1, line) for line_number, line in    \
                        enumerate(open(bashrc)) if alias in line]
        if len(result) == 0:
            fh = open(bashrc, 'a')
            fh.write("\n")
            fh.write(alias)
            fh.close()


if __name__ == '__main__':
    
    pythons = ['python2.4',
               'python2.5',
               'python2.6']
    
    if len(sys.argv) != 2:
        print "Ejecutar: xpyenv <parametro>"
        print "Parametros:                \
        \n python2.4 / Crea un python virtual 2.4   \
        \n python2.5 / Crea un python virtual 2.5   \
        \n python2.6 / Crea un python virtual 2.6   \
        "
    else:
        if sys.argv[1] in pythons:
            pyenv = PyEnv()
            pyenv.doitrightnow(sys.argv[1])
        else:
            print "Parametro no aceptado: %s" % sys.argv[1]
