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

from zopeskel.plone import Plone
from zopeskel.basic_namespace import BasicNamespace
from zopeskel.nested_namespace import NestedNamespace
from zopeskel.base import var
from zopeskel.base import get_var

from addon import AddOn

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

class IWPython(BasicNamespace):
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

