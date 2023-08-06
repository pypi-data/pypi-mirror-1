##############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

import logging, os, shutil, tempfile, urllib2, urlparse
import setuptools.archive_util
import datetime
import sha
import shutil
import zc.buildout
import zc.recipe.egg
from os.path import join
import os
from os.path import dirname, abspath
import ConfigParser


def system(c):
    if os.system(c):
        raise SystemError("Failed", c)



class Recipe:

    def __init__(self, buildout, name, options):
        self.egg = zc.recipe.egg.Egg(buildout, options['recipe'], options)
        self.name, self.options, self.buildout = name, options, buildout

        #get all recipes here to make sure we're the last called
        main = None
        for part, recipe, opt in self.getAllRecipes():
            if recipe == self.options['recipe']:
                main = opt
                if opt.get('mainhostout') == self.name:
                    break
        if main:
            main['mainhostout'] = self.name


        self.buildout_dir = self.buildout.get('buildout').get('directory')
        self.download_cache = self.buildout['buildout'].get('download-cache')
        self.install_from_cache = self.buildout['buildout'].get('install-from-cache')
        self.options['versions'] = self.buildout['buildout'].get('versions','versions')
        self.options['location'] = os.path.join(
            self.buildout['buildout']['parts-directory'],
            'hostout',
            )
        self.optionsfile = join(self.options['location'],'hostout.cfg')
        self.fabfiles = []

        extends = [e.strip() for e in self.options.get('extends','').split() if e.strip()]

        for extension in reversed(extends):
            extension = buildout.get(extension)
            if extension is None:
                continue
            for key in extension:
                if key == 'fabfile':
                    self.fabfiles.append(extension[key])
                if key not in self.options:
                    self.options[key] = extension[key]


        self.options.setdefault('dist_dir','dist')
        self.options.setdefault('buildout','buildout.cfg')
        self.options.setdefault('user','') #get default from .ssh/config
        self.options.setdefault('identity-file',self.options.get('identity_file',''))
        self.options.setdefault('effective-user','plone')
        self.options.setdefault('host', 'localhost')
        self.options.setdefault('password','')
        self.options.setdefault('post-commands', self.options.get('start_cmd',''))
        self.options.setdefault('pre-commands', self.options.get('stop_cmd', ''))
        self.options.setdefault('include', self.options.get('extra_config',''))
        self.options.setdefault('parts','')
        default_path = '~%s/buildout'%self.options['user']
        self.options.setdefault('path', self.options.get('remote_path',''))
#        self.extra_config = [s.strip() for s in self.options.get('extra_config','').split('\n') if s.strip()]
        self.options.setdefault('buildout_location',self.buildout_dir)
        self.options['fabfiles'] = '\n\t'.join(self.fabfiles)



    def install(self):
        logger = logging.getLogger(self.name)

        location = self.options['location']

        if not os.path.exists(location):
            os.mkdir(location)


        config = ConfigParser.ConfigParser()
        config.read(self.optionsfile)

        fp = open(self.optionsfile, 'w+')
        config.write(fp)
        fp.close()
        self.update()

        return self.optionsfile

    def update(self):

        if self.options.get('mainhostout') is not None:
            requirements, ws = self.egg.working_set()
            bin = self.buildout['buildout']['bin-directory']
            extra_paths=[]
            zc.buildout.easy_install.scripts(
                [('hostout', 'collective.hostout.hostout', 'main')],
                ws, self.options['executable'], bin,
                arguments="'%s',sys.argv[1:]"%self.optionsfile,
                extra_paths=extra_paths
#                initialization=address_info,
                )

        config = ConfigParser.RawConfigParser()
        config.optionxform = str
        config.read(self.optionsfile)

        if not config.has_section(self.name):
            config.add_section(self.name)
        if not config.has_section('buildout'):
            config.add_section('buildout')
        for name,value in self.options.items():
            config.set(self.name, name, value)
        config.set('buildout','location',self.buildout_dir)

        if self.options.get('mainhostout') is not None:
            if config.has_section('versions'):
                config.remove_section('versions')
            config.add_section('versions')
            for pkg,info in sorted(self.getVersions().items()):
                    version,deps = info
                    config.set('versions',pkg,version)
            config.set('buildout', 'bin-directory', self.buildout.get('buildout').get('directory'))
            if self.options['dist_dir']:
                config.set('buildout','dist_dir', self.options['dist_dir'])

            packages = [p.strip() for p in self.buildout.get('buildout').get('develop','').split()]
            packages += [p.strip() for p in self.options.get('packages','').split()]
            if not config.has_section('buildout'):
                config.add_section('buildout')
            config.set('buildout', 'packages', '\n   '.join(packages))
        #self.options.setdefault('develop','')

        fp = open(self.optionsfile, 'w+')
        config.write(fp)
        fp.close()
        return self.optionsfile



    def getAllRecipes(self):
        recipes = []

        for part in [p.strip() for p in self.buildout['buildout']['parts'].split()]:
            options = self.buildout.get(part) #HACK
            if options is None or not options.get('recipe'):
                continue
            try:
                recipe,subrecipe = options['recipe'].split(':')
            except:
                recipe=options['recipe']
            recipes.append((part,recipe,options))
        return recipes

    def getVersions(self):
        versions = {}
        for part, recipe, options in self.getAllRecipes():
            egg = zc.recipe.egg.Egg(self.buildout, recipe, options)
            #TODO: need to put in recipe versions too
            requirements, ws = egg.working_set()
            for dist in ws:
                old_version,dep = versions.get(dist.project_name,('',[]))
                if recipe not in dep:
                    dep.append(recipe)
                if dist.version != '0.0':
                    versions[dist.project_name] = (dist.version,dep)
        spec = ""
        return versions
        for project_name,info in versions.items():
            version,deps = info
            spec+='\n'
#            for dep in deps:
#                spec+='# Required by %s==%s\n' % (dep, 'Not Implemented') #versions[dep][0])
            if version != '0.0':
                spec+='%s = %s' % (project_name,version)+'\n'
#            else:
#                spec+='#%s = %s' % (project_name,version)+'\n'
        return spec


# relpath.py
# R.Barran 30/08/2004

import os

def relpath(target, base=os.curdir):
    """
    Return a relative path to the target from either the current dir or an optional base dir.
    Base can be a directory specified either as absolute or relative to current dir.
    """

    if not os.path.exists(target):
        raise OSError, 'Target does not exist: '+target

    if not os.path.isdir(base):
        raise OSError, 'Base is not a directory or does not exist: '+base

    base_list = (os.path.abspath(base)).split(os.sep)
    target_list = (os.path.abspath(target)).split(os.sep)

    # On the windows platform the target may be on a completely different drive from the base.
    if os.name in ['nt','dos','os2'] and base_list[0] <> target_list[0]:
        raise OSError, 'Target is on a different drive to base. Target: '+target_list[0].upper()+', base: '+base_list[0].upper()

    # Starting from the filepath root, work out how much of the filepath is
    # shared by base and target.
    for i in range(min(len(base_list), len(target_list))):
        if base_list[i] <> target_list[i]: break
    else:
        # If we broke out of the loop, i is pointing to the first differing path elements.
        # If we didn't break out of the loop, i is pointing to identical path elements.
        # Increment i so that in all cases it points to the first differing path elements.
        i+=1

    rel_list = [os.pardir] * (len(base_list)-i) + target_list[i:]
    return os.path.join(*rel_list)

