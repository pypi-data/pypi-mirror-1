# -*- coding: utf-8 -*-
"""Recipe ant"""

import logging
import subprocess
import os
import zc.buildout
import sys

class Recipe(object):
    """This recipe is used by zc.buildout"""

    def __init__(self, buildout, name, options):
        self.name, self.options = name, options

        ant_default = 'ant'

        verbosity = buildout['buildout'].get('verbosity', 0)
        if verbosity:
            verbosity = verbosity[0] 
        options['verbosity'] = str(verbosity)
        options['ant'] = options.get('ant', ant_default).strip()
        options['ant-home'] = options.get('ant-home', '').strip()
        options['ant-options'] = ' '.join(options.get('ant-options','').split())
        options['location'] = os.path.join(
            buildout['buildout']['parts-directory'],
            self.name)

        if options['ant'] != ant_default and not os.path.exists(options['ant']):
            raise zc.buildout.UserError(
                    'Ant executable not found in %s.' % options['ant'])

        if options['ant-home'] and not os.path.exists(options['ant-home']):
            raise zc.buildout.UserError(
                    'ANT_HOME %s not found.' % options['ant-home'])

        # construct the classpath var the os relative way
        classpath = options.get('classpath', '').split()
        options['classpath'] = ''
    	if classpath:
            if sys.platform.startswith('win'):
                sep = ';'
            else:
                sep = ':'
	
            for path in classpath:
                if not os.path.exists(path):
                    raise zc.buildout.UserError(
                            'Classpath %s does not exist.' % path)
                if options['classpath']:
                    options['classpath'] = options['classpath'] + sep + path
                else:
                    options['classpath'] = path

    def run(self, cmd, env=None):
        log = logging.getLogger(self.name)

        environ = os.environ.copy()
        environ.update(env)

        try:
            ant = subprocess.Popen(
                cmd.split(),
                env=environ,
                stdout=subprocess.PIPE)
            returnmessage = ant.communicate()[0]
            if int(self.options['verbosity']) > 0:
                log.info(returnmessage)
        except Exception, msg:
            log.error(
                'Error running command: %s with environment %s' % 
                (cmd, str(env))
                )
            raise zc.buildout.UserError('System error: %s' % msg)

        if ant.returncode != 0:
            raise zc.buildout.UserError('System error: %s' % returnmessage)
        else:
            log.info('Build successful')

    def install(self):
        """installer"""
        classpath = ''
        if len(self.options['classpath']) > 0:
            classpath = '-lib %s' % self.options['classpath']

        self.run('%(ant)s %(ant_options)s %(classpath)s' % {
                'ant_home' : self.options['ant-home'],
                'ant' : self.options['ant'],
                'ant_options' : self.options['ant-options'],
                'classpath' : classpath,
                }, env = {'ANT_HOME' : self.options['ant-home']})

        return (self.options['location'],)

    def update(self):
        """updater"""
        pass
