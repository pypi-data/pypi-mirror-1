266# -*- coding: utf-8 -*-
#
# Copyright (c) 2007 by BlueDynamics Alliance, Klein & Partner KEG, Austria
# parts Copyright (c) 2006-2007 Zope Corporation and Contributors.
#
# Zope Public License (ZPL)
__author__ = """Jens Klein <jens@bluedynamics.com>"""
__docformat__ = 'plaintext'

import logging
import os
import re
import shutil
import copy
import sets 
import zc.buildout
import zc.recipe.egg
from plone.recipe.dzhandle.templates import clientpatterns

class Recipe(object):
    """recipe for dzhandle usage."""
    
    dzhandle = '/usr/bin/dzhandle'    
    
    def __init__(self, buildout, name, options):
        self.logger = logging.getLogger(name) 
        self.buildout = buildout
        self.name = name
        self.directories = sets.Set()
        self.options = options

        # global eggs
        self.egg = zc.recipe.egg.Egg(buildout, options['recipe'], options)
        
        # defaults
        self.options.setdefault('locationtype', 'buildout')
        self.options.setdefault('zopetype', 'standalone')
        self.options.setdefault('version', '2.10')
        z2loc = '/usr/lib/zope%s' % self.options.get('version').strip()
        self.options.setdefault('zope2-location', z2loc) 
                                

        # validation 
        if options.get('version') not in ['2.9', '2.10']:
            raise zc.buildout.UserError, "wrong 'version' given."
        if options.get('zopeuser', None) is None:
            raise zc.buildout.UserError, "You need to provide option 'zopeuser=username:passwort'!"               
        if self.options.get('zopetype') not in ('standalone', 'client', 'server'):
            raise zc.buildout.UserError, "wrong 'zopetype' given."
        if self.options.get('zopetype', '') == 'server':
            raise NotImplemented, "zopetype 'server'."
            
        
    def install(self):
        """Install creates a new instance and configuration."""
        self.createInstance()
        self.update()
        return self.instancehome
    
    def update(self):
        """Update creates new configuration files in an existing instance"""
        self.createSymlinks()
        self.patchBinaries()
        self.createZEOClientConfiguration()
        self.createPackageIncludes()
        return self.instancehome
        
    def createInstance(self):
        """creates a blank instance using dzhandle."""
        task = 'make-instance'            
        args = []
        ltype = self.options.get('locationtype')
        if ltype != 'buildout':                        
            args.append(self.options.get('instancename', self.name))
        else:
            args.append(self.instancehome)            
        sudo = ltype=='system'            
        args.append('-m manual')
        args.append('-u %s' % self.options.get('zopeuser'))
        self.execute(task, sudo=sudo, *args)

    def createZEOClientConfiguration(self):
        """creates a fresh zope.conf according to the settigs given."""
        confdir = os.path.join(self.instancehome, 'etc')
        confdeb = os.path.join(confdir, 'zope.conf.debian')
        conftarget = os.path.join(confdir, 'zope.conf')

        # if zope.conf.debian does not exist copy zope.conf to zope.conf.debian
        if not os.path.exists(confdeb):
            assert(os.path.exists(conftarget))
            assert(os.path.isfile(conftarget))
            shutil.copyfile(conftarget, confdeb)            
            self.logger.info('copied zope.conf to zope.conf.debian. latter will' 
                             ' be used a template for zope.conf')
        assert(os.path.isfile(confdeb))

        # use the .debian as template
        deblines = open(confdeb, 'r').readlines()
        targetlines = self.handleConf(deblines, clientpatterns)
        
        targetfile = open(conftarget, 'w')
        targetfile.writelines(targetlines)
        targetfile.close()
        
    def handleConf(self, lines, patterns):
        """takes a conf file and apply patterns to it."""

        ###############################
        # first pass: simple line replacement
        newlines = []
        handled = []
        # 1.1 replace
        for line in lines:
            if line.strip().startswith('#') or line.strip() == '':
                continue
            newline = line
            for lpat in patterns:                
                if lpat['type'] != 'line':
                    continue
                if 'replace' in lpat['mode'] and \
                   lpat['pattern'] in line and \
                   self.options.get(lpat['option'], None):                    
                    newline = self.createLineFromOption(lpat)
                    handled.append(lpat['option'])     
                    break             
            newlines.append(newline)

        # 1.2 handle options left to add 
        for lpat in patterns:
            if lpat['type'] != 'line':
                continue
            if lpat['option'] in handled or \
               'add' not in lpat['mode'] or \
               self.options.get(lpat['option'], None) is None:
                continue
            newline = self.createLineFromOption(lpat)
            newlines.append(newline)
            
        ##############################
        # second pass: handle sections
        lines = copy.copy(newlines)
        newlines = []
        handled = []
        currentsection = None
        replaced = False
        # 1.1 replace existing
        for line in lines:
            if currentsection is not None:                            
                # handle inside section
                name, lpat, sectiondef = currentsection
                sectiondef['name'] = name
                if not replaced:
                    tpl = lpat['templates'][sectiondef['type'].strip()]
                    result = tpl % sectiondef
                    newlines.append(result)
                    handled.append( '%s_%s' % (lpat['optionprefix'], name) )
                    replaced = True
                if line.find('</%s>' % lpat['sectionname']) >= 0:
                    newlines.append(line)
                    currentsection = None
                    replaced = False
                    continue
            else:
                newlines.append(line)
                # find sections                
                for lpat in patterns:
                    if lpat['type'] != 'sections':
                        continue   
                    sections = self.sections(lpat['optionprefix'], 'dict')
                    if line.find('<') >= line.find(lpat['sectionname']):
                        continue
                    namestart = line.find(lpat['sectionname']) + \
                                len(lpat['sectionname'])
                    name = line[namestart: line.find('>')].strip()
                    if name in sections.keys():
                        # found the section
                        currentsection = name, lpat, sections[name]

        # 1.2 add sections not replaced
        for lpat in patterns:
            if lpat['type'] != 'sections':
                continue   
            sections = self.sections(lpat['optionprefix'], 'dict')
            for name in sections:
                if '%s_%s' % (lpat['optionprefix'], name) in handled:
                    continue
                sectiondef = sections[name]
                sectiondef['name'] = name
                newlines.append('<%s %s>\n' % (lpat['sectionname'], name))
                tpl = lpat['templates'][sectiondef['type'].strip()]
                result = tpl % sectiondef
                newlines.append(result)
                newlines.append('</%s>\n' % lpat['sectionname'])
        return newlines
    
    def createLineFromOption(self, lpat):
        otype = lpat.get('optiontype', None)
        if otype is not None:
            option = self.complexOption(lpat['option'], otype)
        else:
            option = self.options[lpat['option']]
        if otype == 'list':
            newline = [(lpat['replace'] % l) for l in option]
            newline = '\n'.join(newline) + '\n'
        else:
            newline = lpat['replace'] % option
        return newline    
    
    
    def sections(self, prefix, type):
        """list all sections from options"""        
        result = {}
        for optionkey in self.options.keys():
            if optionkey.startswith(prefix):
                key = optionkey[len(prefix):]
                value = self.complexOption(optionkey, type)
                result[key] = value
        return result
    
    def complexOption(self, name, type='list'):
        """a way to make a list or dict from a dumb string.
        
        for a list just put one value per line
        
        foobar = 
            foo
            bar
            baz
            
        results in ['foo', 'bar', 'baz']
        
        for a dict put one definiton per line:
        
        foobar = 
            foo: bar
            baz: baaz
            
        results in {'foo': 'bar', 'baz': 'baaz'}
        
        *sigh*, would like to have this in zc.buildout itself.
        
        @param type: one out of ('list', 'dict').
        """
        value = self.options.get(name, None)
        if value is None:
            return None
        value = [l.strip() for l in value.split('\n') if l.strip()]
        if type == 'dict':
            result = {}
            for item in value:
                key, item = item.split(':', 1)
                result[key.strip()] = item.strip()
            value = result
        return value
            
    def createPackageIncludes(self):
        """ZCML to include packages. Taken from plone.recipe.zope2install. 

        This method is Copyright (c) 2006-2007 Zope Corporation and Contributors.
        """        
        location = self.instancehome
        zcml = self.options.get('zcml')
        
        if zcml:
            sitezcml_path = os.path.join(location, 'etc', 'site.zcml')
            if not os.path.exists(sitezcml_path):
                # Zope 2.9 does not have a site.zcml so we copy the
                # one out from Five.
                zope2_location = self.options['zope2-location']
                skel_path = os.path.join(zope2_location, 'lib', 'python',
                                         'Products', 'Five', 'skel',
                                         'site.zcml')
                shutil.copyfile(skel_path, sitezcml_path)

            includes_path = os.path.join(location, 'etc', 'package-includes')
            if not os.path.exists(includes_path):
                # Zope 2.9 does not have a package-includes so we
                # create one.
                os.mkdir(includes_path)

            zcml = zcml.split()
            if '*' in zcml:
                zcml.remove('*')
            else:
                shutil.rmtree(includes_path)
                os.mkdir(includes_path)

            n = 0
            package_match = re.compile('\w+([.]\w+)*$').match
            for package in zcml:
                n += 1
                orig = package
                if ':' in package:
                    package, filename = package.split(':')
                else:
                    filename = None

                if '-' in package:
                    package, suff = package.split('-')
                    if suff not in ('configure', 'meta', 'overrides'):
                        raise ValueError('Invalid zcml', orig)
                else:
                    suff = 'configure'

                if filename is None:
                    filename = suff + '.zcml'

                if not package_match(package):
                    raise ValueError('Invalid zcml', orig)

                path = os.path.join(
                    includes_path,
                    "%3.3d-%s-%s.zcml" % (n, package, suff),
                    )
                open(path, 'w').write(
                    '<include package="%s" file="%s" />\n'
                    % (package, filename)
                    )            
                
    def patchBinaries(self):
        requirements, ws = self.egg.working_set()
        egg_locations = [e.location for e in ws]
        location = self.instancehome
        path =":".join(egg_locations)
        for script_name in ('runzope', 'zopectl'):
            script_path = os.path.join(location, 'bin', script_name)
            script = open(script_path).readlines()
            newscript = []
            for line in script:                
                line = line.rstrip()
                if line.strip().startswith("PYTHONPATH="):
                    newscript.append('PYTHONPATH=$SOFTWARE_HOME:'+path+':$PYTHONPATH')
                else:
                    newscript.append(line)
            newscript = '\n'.join(newscript)
            f = open(script_path, 'w')
            f.write(newscript)
            f.close()        
                
    # some helpers below here

    def execute(self, task, *args, **kw):
        """executes dzhandle."""
        args = ' '.join(args)
        serviceuser = self.options.get('serviceuser', '') 
        if serviceuser != '':
            serviceuser = "-u %s " % serviceuser
        command = '%s -z%s %s%s %s' % (self.dzhandle, 
                                        self.options.get('version'),
                                        serviceuser, 
                                        task, 
                                        args)
        if kw.get('sudo', False):
            command = 'sudo %s' % command
        self.logger.info('command: %s' % command)
        os.system(command)
        
    def createSymlinks(self):
        """creates symlinks in bin and if needed in parts"""
        ltype = self.options.get('locationtype', 'buildout').strip()
        assert(ltype in ('system', 'user', 'buildout'))
        if ltype != 'buildout':
            # symlink instance to parts directory
            target = os.path.join(
                self.buildout['buildout']['parts-directory'],
                self.name
            )
            ln = "ln -s %s %s" % (self.instancehome, target)
            os.system(ln)
        # symlink zopectl 
        source = os.path.join(self.instancehome, 'bin', 'zopectl')
        target = os.path.join(
                self.buildout['buildout']['bin-directory'],
                ('%sctl' % self.options.get('instancename', self.name)),
        )
        ln = "ln -s %s %s" % (source, target)
        os.system(ln)
        
    @property
    def instancehome(self):
        if self.options.get('location', None) is not None:
            return self.options['location']
        
        ltype = self.options.get('locationtype', 'buildout').strip()
        assert(ltype in ('system', 'user', 'buildout'))
        if ltype == 'buildout':
            self.options['location'] = os.path.join(
                self.buildout['buildout']['parts-directory'],
                self.options.get('instancename', self.name),
            )
            return self.options['location']
        elif ltype == 'system':
            base = '/var/lib/zope%s/instance' % \
                   self.options.get('version').strip()
        elif ltype == 'user':
            base = os.path.expanduser('~/zope/instance')
            base += '/zope%s' % self.options.get('version').strip()
        self.options['location'] = '%s/%s' % (base, 
                                              self.options.get('instancename', 
                                                               self.name))
        return self.options.get('location', None) 

            
        
    
