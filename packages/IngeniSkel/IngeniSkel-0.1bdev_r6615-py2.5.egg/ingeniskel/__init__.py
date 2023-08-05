# -*- coding: utf-8 -*-
## Copyright (C)2007 Ingeniweb

## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.

## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

## You should have received a copy of the GNU General Public License
## along with this program; see the file COPYING. If not, write to the
## Free Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
""" Template definitions
"""
import os
import shutil
import copy

from paste.script import templates

from zopeskel import Plone
from zopeskel import Namespace
from zopeskel import NestedNamespace
from zopeskel import var
from zopeskel import get_var

class IWPloneProject(templates.Template):
    """ Generates a Plone 3 project tree with Ingeniweb packages
    """
    _template_dir = 'templates/iw_plone_project'
    summary = 'A Plone 3 project tree for Ingeniweb projects'
    use_cheetah = True

    vars = [var('project_name', 'Project Name'),
            var('project_repo', 'Project Subversion root'),
            var('zope_user', 'Zope root admin user', default='admin'),
            var('zope_password', 'Zope root admin password'),
            var('http_port', 'HTTP port', default=8080),
            var('debug_mode', 'Should debug mode be "on" or "off"?', default='off'),
            var('verbose_security', 'Should verbose security be "on" or "off"?', default='off')]

class IWPython(Namespace):
    """ Generates a pure Python lib for 'iw' namespace
    """
    _template_dir = 'templates/iw_python'
    summary = "A project with a namespace package"
    required_templates = ['basic_namespace']

    vars = [
        var('namespace_package', 'Namespace package', default='iw'),
        var('package', ('The package contained namespace package '
                        '(like example)'), default='example'),
        var('version', 'Version', default='0.1'),
        var('description', 'One-line description of the package'),
        var('author', 'Author name', default='Ingeniweb'),
        var('author_email', 'Author email',
            default='support@ingeniweb.com'),
        var('keywords', 'Space-separated keywords/tags'),
        var('url', 'URL of homepage'),
        var('license_name', 'License name', default='GPL'),
        var('zip_safe', 'True/False: if the package can be distributed '
            'as a .zip file', default=False),
        ]

class IWRecipe(NestedNamespace):
    _template_dir = 'templates/iw_recipe'
    summary = "A recipe project"
    required_templates = []
    use_cheetah = True

    vars = copy.deepcopy(NestedNamespace.vars)

    get_var(vars, 'namespace_package').default = 'iw'
    get_var(vars, 'namespace_package2').default = 'recipe'
    get_var(vars, 'author').default = 'Ingeniweb'
    get_var(vars, 'author_email').default = 'support@ingeniweb.com'


class AddOn(Namespace):
    required_templates = []

    def getProjectName(self):
        if not os.path.isfile('config.py'):
            raise RuntimeError('You cant create a content without a config.py')
        projectname = None
        fd = open('config.py')
        for line in fd:
            if line.startswith('PROJECTNAME'):
                projectname = line.split('=')[1]
                projectname = projectname.strip()
                projectname = projectname.replace('"','')
                projectname = projectname.replace("'",'')
        fd.close()
        if not projectname:
            raise RuntimeError("Can't retrieve project name in config.py")
        return projectname

    def post(self, command, output_dir, vars):
        basedir = vars['project']
        print 'Moving package %s to product %s' % (vars['project'], vars['product_name'])
        for dirname in os.listdir(basedir):
            path = os.path.join(basedir, dirname)
            print '  Copying %s to %s' % (path, dirname)
            if not os.path.isdir(dirname):
                shutil.copytree(path, dirname)
                if os.path.isdir('.svn'):
                    os.popen('svn add %s' % dirname)
            else:
                for filename in os.listdir(path):
                    src = os.path.join(path, filename)
                    dst = os.path.join(dirname, filename)
                    if not os.path.isfile(dst):
                        shutil.copyfile(src, dst)
                        if os.path.isdir(os.path.join(dirname, '.svn')):
                            os.popen('svn add %s' % dst)
                    else:
                        print '    Skipping %s. file exist' % dst
        print 'Removing %s' % basedir
        shutil.rmtree(basedir)


class IWContent(AddOn):

    _template_dir = 'templates/iw_content'
    summary = "A content type"

    vars = [
        var('author', 'Author name', default='Ingeniweb'),
        var('author_email', 'Author email',
            default='support@ingeniweb.com'),
        ]

    def pre(self, command, output_dir, vars):
        if not os.path.isdir('tests'):
            raise RuntimeError('You cant create a content without a tests dir')
        if not os.path.isdir('doctests'):
            raise RuntimeError('You cant create a content without a doctests dir')
        vars['type_name'] = vars['project'].lower()
        vars['class_name'] = vars['project']
        projectname = self.getProjectName()
        if '.' in projectname:
            # product is a namespace
            vars['namespace'] = projectname
            product_name = [n.title() for n in projectname.split('.')]
            product_name = ''.join(product_name)
            vars['product_name'] = product_name
        else:
            # product is a standard zope Product
            vars['namespace'] = 'Products.%s' % projectname
            vars['product_name'] = projectname

class IWPlone(Plone):
    """A plone 3 namespaced product"""
    use_cheetah = True
    vars = copy.deepcopy(Plone.vars)
    _template_dir = 'templates/iw_plone'
    summary = "A Plone 3 namespaced product"
    
    get_var(vars, 'namespace_package').default = 'iw'
    get_var(vars, 'author').default = 'Ingeniweb'
    get_var(vars, 'author_email').default = 'support@ingeniweb.com'
    get_var(vars, 'url').default = ('https://ingeniweb.svn.sourceforge.net/'
                                    'svnroot/ingeniweb/iw.example')

