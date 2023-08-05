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
""" Add on
"""
import os
import shutil
import re
import difflib

from zopeskel.basic_namespace import BasicNamespace

class AddOn(BasicNamespace):
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

    def _diff(self, target, addon):
        """marge addon into src"""
        # diff that sees if the file is a tagged file
        # if so, inject the content just before the end bracket
        # otherwised, appends
        if addon in target:
            return target
        # let's find the diff, then merge it
        def _merge(line):
            if line[:2] in ('+ ', '- ', '  '):
                return line[2:]
            return ''
        delta = [_merge(el) for el in 
                 difflib.ndiff(target.splitlines(1), 
                               addon.splitlines(1))]
        # let's inject it
        return ''.join(delta)
                
    def _check_file(self, filename, path, dirname):
        """work on a file"""   
        src = os.path.join(path, filename)
        if os.path.isdir(src):
            # let's recurse
            for element in os.listdir(src):
                dir_ = os.path.split(src)[-1]
                subdirname = os.path.join(dirname, dir_)
                if not os.path.exists(subdirname):
                    os.mkdir(subdirname)
                self._check_file(element, src, subdirname)
            return

        dst = os.path.join(dirname, filename)
        if not os.path.exists(dst):
            shutil.copyfile(src, dst)
            if os.path.isdir(os.path.join(dirname, '.svn')):
                os.popen('svn add %s' % dst)
        else:
            dst_content = open(dst).read()
            src_content = open(src).read()
            if dst_content == src_content: 
                print '    Skipping %s. file exist' % dst
            else:
                print '    Making diff for %s' % dst
                final_content = self._diff(dst_content, src_content)
                f = open(dst, 'w')
                try:
                    f.write(final_content)
                finally:
                    f.close() 

    def post(self, command, output_dir, vars):
        """post-templating"""
        basedir = vars['project']
        print 'Moving package %s to product %s' % (vars['project'], 
                                                   vars['product_name'])
        
        package_dir = '.'
        for element in os.listdir(basedir):
            path = os.path.join(basedir, element)
            print '  Copying %s to %s' % (path, package_dir)
            if not os.path.isdir(path):
                # single file
                self._check_file(element, basedir, package_dir)
            else:
                # subfolder
                extracted_folder = os.path.split(path)[-1]
                subfolder = os.path.join(package_dir, extracted_folder)
                if not os.path.exists(subfolder):
                    os.mkdir(subfolder)
                if os.path.exists(os.path.join(package_dir, '.svn')):
                    os.popen('svn add %s' % subfolder)
                # copying subfolder elements
                for filename in os.listdir(path):
                    self._check_file(filename, path, subfolder)

        print 'Removing %s' % basedir
        shutil.rmtree(basedir)

