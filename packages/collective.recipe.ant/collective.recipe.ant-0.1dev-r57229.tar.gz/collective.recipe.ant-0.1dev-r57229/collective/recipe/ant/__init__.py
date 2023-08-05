# -*- coding: utf-8 -*-
"""Recipe ant"""

import logging
import subprocess
import os
import zc.buildout
import sys

ANT_DEFAULT = 'ant'
CLASSPATH_SEP = sys.platform.startswith('win') and ';' or ':'

class Recipe(object):
    """This recipe is used by zc.buildout"""

    def __init__(self, buildout, name, options):
        self.name, self.options = name, options

        verbosity = buildout['buildout'].get('verbosity', 0)
        if verbosity:
            verbosity = verbosity[0] 
        options['verbosity'] = str(verbosity)
        options['ant'] = options.get('ant', ANT_DEFAULT).strip()
        options['ant-home'] = options.get('ant-home', '').strip()
        options['ant-options'] = ' '.join(options.get('ant-options','').split())
        options['location'] = os.path.join(
            buildout['buildout']['parts-directory'],
            self.name)

        # construct the classpath var the os relative way
        classpath = options.get('classpath', '').strip().split()
        options['classpath'] = ''
    	if classpath:
            options['classpath'] = CLASSPATH_SEP.join(classpath)


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
        if self.options['ant'] != ANT_DEFAULT and not os.path.exists(self.options['ant']):
            raise zc.buildout.UserError(
                    'Ant executable not found in %s.' % options['ant'])

        for cp in self.options['classpath'].split(CLASSPATH_SEP):
            
            if cp.strip() and not os.path.exists(cp.strip()):
                raise zc.buildout.UserError(
                    'Classpath %s does not exist.' % cp)

        if self.options['ant-home'] and not os.path.exists(self.options['ant-home']):
            raise zc.buildout.UserError(
                    'ANT_HOME %s not found.' % options['ant-home'])

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
