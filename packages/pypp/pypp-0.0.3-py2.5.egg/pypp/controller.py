#!/usr/bin/env python
""" Controller class
    project: pypp
    
    @author: Jean-Lou Dupont
"""

__author__  = "Jean-Lou Dupont"
__version__ = "$Id: controller.py 13 2009-03-07 15:40:10Z jeanlou.dupont $"

__all__ = ['Controller']

import os
import sys

from preprocessor import Tpl

class Controller(object):
    """ Controller class
    """
    #__slots__ = ['_processed', '_loader']
    
    def __init__(self):
        
        #load class
        self._loader = None
        self._processed = {}
    
    def handle_import_module(self, name, rpath, path, file, desc, global_scope):
        """ Callback for the PEP302 import_module function 
        """
        #paranoia
        if (name in self._processed):
            return None
        
        self._processed[name] = path
    
        #Perform the preprocessing
        if (file):
            processed_file = self.preprocessModule(name, file)
        else:
            processed_file = self.preprocessPackage(name, path)
    
        #Finally load
        try:
            return self._loader(name, processed_file, rpath, desc, global_scope)
        except ImportError:
            pass #pass-through
        
        return None

    def preprocessModule(self, name, file):
        """ Preprocess a module
        """
        #get rid of originating file because
        # we will anyway generate a new one
        path = file.name
        file.close()
        return self._preprocessFile(name, path)
        

    def preprocessPackage(self, name, path):
        """ Preprocess a package
        """
        return self._preprocessFile(name, path)


    def _preprocessFile(self, name, path):
        """ Preprocess a source file.
        """

        #let's make sure we really need to process the file
        processed_path = path + '.pypp'
        
        if (self._isFresh(path, processed_path)):
            #print "fresh: name(%s)" % name
            return self._returnFile( processed_path )

        #first, read source file in
        try:
            file = open(path)
            text = file.read()
        except:
            raise ImportError
        
        #next, determine if we have a directive .pypp
        # If we can't find one, we still have to return
        # a valid file object to the caller.
        if (text.find("#.pypp")==-1):
            return file

        #we are finished with the source file
        #because at this point we know we'll have to
        #deal with a compiled template.
        file.close()
        
        # if an error occurs, let it trickle up
        # TODO is there a better to handle exceptions here??
        dir = os.path.dirname(path)
        rendered = Tpl(text, dirs=dir).render()

        try:
            file = open( processed_path, "w")
            file.write(rendered)
        except Exception,e:
            raise RuntimeError("pypp: error writing rendered file, path(%s) exception(%s)" % (processed_path, e))
        finally:
            file.close()
            
        # lastly, re-open the file but this time in read-only mode
        try:
            file = open(processed_path)
        except Exception,e:
            raise RuntimeError("pypp: error opening rendered file, path(%s) exception(%s)" % (processed_path, e) )
        
        return file

    def _returnFile(self, filepath):
        """ Opens 
        """
        try:
            file = open(filepath,"r")
            return file
        except:
            raise ImportError

    def _isFresh(self, source_filepath, compiled_filepath):
        """ Verifies if the compiled source file is fresh.
            If we have an error of any sort, assume we have
            to process the file anyhow. This covers the cases:
            - no processed file is available yet
            - no processed file is available and there won't be any 
        """
        try:
            s_mtime = os.path.getmtime(source_filepath)
            c_mtime = os.path.getmtime(compiled_filepath)
        except:
            return False
        
        return (c_mtime > s_mtime)

    def _processed(self):
        """ for debugging purpose
        """
        for i in self._processed:
            yield i
        