#!/usr/bin/env python
""" Preprocessor class
    project: pypp
    
    @author: Jean-Lou Dupont
"""
__author__  = "Jean-Lou Dupont"
__version__ = "$Id: preprocessor.py 7 2009-03-02 20:30:01Z jeanlou.dupont $"

__all__ = ['Tpl']

import os
import sys

try:
    from mako.template import Template
    from mako.lookup import TemplateLookup
except:
    print "pypp: Mako template package not found. Please install"
    sys.exit(1)
 
class Tpl(object):
    """ Template based on the Mako engine
    """
    def __init__(self, input, dirs = None):
        """ The directory path of the input file
            serves as configuration for the template
            directory by default. If *dirs* is specified,
            it takes precedence.
            
            @param input: the input file (complete file path)
            @param dirs: the template directory list   
        """
        self.input = input
        if dirs:
            self.dirs = dirs
        else:
            self.dirs = [ os.path.dirname( input ) ]
            
    def render(self, **params):
        """ Performs the preprocessing.
            @param params: the input parameters
            @return: rendered text            
        """
        lookup = TemplateLookup(directories = self.dirs) if self.dirs else None
        tpl = Template(text=self.input, lookup=lookup)
        return tpl.render(**params)
