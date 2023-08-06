#!/usr/bin/env python

# pylint: disable-msg=W0221,R0201
"""

doapfiend_vcs
================

This is a plugin for interfacing with VCS (Version Control Systems)
such as CVS, SVN, Git, Mercurial, Bazaar etc.

You don't need to know what type of VCS the project uses.

This is all very basic, it doesn't check to make sure your commands
are valid for the particular type of repository you're using.

It's meant mainly to 'ls' a repository or do a 'checkout' and to
show how a more sophisticated plugin could be made using proper
subversion libraries with Python bindings for example.

This is totally untested with Windows and almost certainly won't
work as-is.

Implemented so far:
    CVS
    SVN

TODO:
    Add arch, bazaar, hg
    Use something other than os.system that works on all Python >=2.3
"""

import os
import logging

from doapfiend.plugins.base import Plugin
from doapfiend.doaplib import load_graph


__docformat__ = 'epytext'

LOG = logging.getLogger('doapfiend')


def vcs_cmd(doap, cmd):
    '''
    Run VCS commands

    Note: Currently it will run the command on the first repository found.
    It is possible DOAP may have more than one repository type, but it
    isn't clear if that is valid or not. The reasoning being that DOAP
    should be a record of your current project so having an old repository
    may not be a good idea.

    @param doap_graph: DOAP in RDF/XML serialization
    @type doap_graph: string

    @rtype: string
    @returns: output of VCS command

    '''
    doap_graph = load_graph(doap)
    vcs = get_repo(doap_graph)
    if not vcs:
        return ''
    if vcs == 'svn':
        return svn_cmd(cmd, doap_graph)
    elif vcs == 'cvs':
        return cvs_cmd(cmd, doap_graph)

def get_repo(doap_graph):
    '''
    Return repository type and URL
    The type will also be the command-line name
    svn, cvs, git, arch, hg, bzr

    @param doap_graph: DOAP in RDF/XML serialization
    @type doap_graph: string

    @rtype: string
    @returns: repository type

    '''
    #XXX: Show warning if there are more than one repository types.
    if doap_graph.svn_repository is not None:
        if doap_graph.svn_repository.location is not None:
            return 'svn'
    if doap_graph.cvs_repository is not None:
        if doap_graph.cvs_repository.module is not None:
            return 'cvs'
    else:
        LOG.error('No repository found.')
        return ''
    
def svn_cmd(cmd, doap_graph):
    '''
    Execute an subversion command and return the results.

    @param doap_graph: DOAP in RDF/XML serialization
    @type doap_graph: string

    @rtype: string
    @returns: repository type
    '''
    if hasattr(doap_graph.svn_repository, 'location'):
        url = getattr(doap_graph.svn_repository, 'location')
        url = url.resUri
        parts = cmd.split()
        #If they give a directory, append it to the 'location' URL
        if len(parts) >1 :
            url += '/' + parts[1]
            cmd = parts[0]
        os.system('svn %s %s' % (cmd, url))
        return ''
    else:
        LOG.error('SVN: No location URL found.')
        return ''

def cvs_cmd(cmd, doap_graph):
    '''
    Execute a CVS command and return the results.

    @param cmd: An VCS command such as 'ls', 'checkout' etc.
    @type cmd: string

    @param doap_graph: DOAP in RDF/XML serialization
    @type doap_graph: string

    @rtype: string
    @returns: Results of command output.
    '''
    if hasattr(doap_graph.cvs_repository, 'anon_root'):
        url = getattr(doap_graph.cvs_repository, 'anon_root')
        #url = url.resUri
        LOG.debug('CVS anon-root: %s' % url)
    else:
        LOG.error('No anon-root found.')
        return ''
    if hasattr(doap_graph.cvs_repository, 'module'):
        module = getattr(doap_graph.cvs_repository, 'module')
        LOG.debug('CVS module: %s' % module)
    else:
        LOG.error('No module found.')
        return ''
    #Login to repository first
    os.system('cvs -d%s login' % url)
    os.system('cvs -d%s %s %s' % (url, cmd, module))
    return ''

class VCSPlugin(Plugin):

    """Class for getting a VCS URL from DOAP and executing a VCS command"""

    name = "vcs"
    enabled = False
    enable_opt = None

    def __init__(self):
        '''Setup VCSPlugin class'''
        super(VCSPlugin, self).__init__()
        self.options = None
            
    def add_options(self, parser, output, search):
        '''Add plugin's options to doapfiend's opt parser'''
        output.add_option('--%s' % self.name,
                action='store', 
                dest=self.enable_opt,
                metavar='VCS_CMD',
                help='Run VCS command if repository is found.')
        return parser, output, search

    def serialize(self, doap_graph, color=False):
        '''
        Serialize DOAP as HTML

        @param doap_graph: DOAP in RDF/XML serialization
        @type doap_graph: string

        @param color: Syntax highlighting (Bash) with Pygments
        @type color: boolean 

        @rtype: unicode
        @returns: DOAP as HTML

        '''
        return vcs_cmd(doap_graph, self.options.enable_plugin_vcs)
