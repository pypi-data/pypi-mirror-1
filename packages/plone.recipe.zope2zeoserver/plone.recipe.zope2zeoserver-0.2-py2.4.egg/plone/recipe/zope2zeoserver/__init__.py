##############################################################################
#
# Copyright (c) 2006-2007 Zope Corporation and Contributors.
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

import os, re, shutil
import zc.buildout
import zc.recipe.egg

class Recipe:

    def __init__(self, buildout, name, options):
        self.egg = zc.recipe.egg.Egg(buildout, options['recipe'], options)
        self.buildout, self.options, self.name = buildout, options, name

        options['location'] = os.path.join(
            buildout['buildout']['parts-directory'],
            self.name,
            )
        options['bin-directory'] = buildout['buildout']['bin-directory']
        options['scripts'] = '' # suppress script generation.

    def install(self):
        options = self.options
        location = options['location']

        requirements, ws = self.egg.working_set()
        ws_locations = [d.location for d in ws]

        if os.path.exists(location):
            shutil.rmtree(location)

        # What follows is a bit of a hack because the instance-setup mechanism
        # is a bit monolithic. We'll run mkzeoinstance and then we'll
        # patch the result. A better approach might be to provide independent
        # instance-creation logic, but this raises lots of issues that
        # need to be stored out first.
        mkzeoinstance = os.path.join(options['zope2-location'],
                                     'utilities', 'mkzeoinstance.py')

        assert os.spawnl(
            os.P_WAIT, options['executable'], options['executable'],
            mkzeoinstance, location,
            ) == 0

        try:
            # Save the working set:
            open(os.path.join(location, 'etc', '.eggs'), 'w').write(
                '\n'.join(ws_locations))

            # Make a new zeo.conf based on options in buildout.cfg
            self.build_zeo_conf()
            
            # Patch extra paths into binaries
            self.patch_binaries(ws_locations)

            # Install extra scripts
            self.install_scripts(ws_locations)

        except:
            # clean up
            shutil.rmtree(location)
            raise

        return location

    def update(self):
        options = self.options
        location = options['location']

        requirements, ws = self.egg.working_set()
        ws_locations = [d.location for d in ws]

        if os.path.exists(location):
            # See is we can stop. We need to see if the working set path
            # has changed.
            saved_path = os.path.join(location, 'etc', '.eggs')
            if os.path.isfile(saved_path):
                if (open(saved_path).read() !=
                    '\n'.join(ws_locations)
                    ):
                    # Something has changed. Blow away the instance.
                    self.install()

            # Nothing has changed.
            return location

        else:
            self.install()

        return location

    def build_zeo_conf(self):
        """Create a zeo.conf file
        """
        
        options = self.options
        location = options['location']
        
        instance_home = location
        
        zope_conf_path = options.get('zeo-conf', None)
        if zope_conf_path is not None:
            zope_conf = "%%include %s" % os.path.abspath(zope_conf_path)
        else:
            zeo_address = options.get('zeo-address', '8100')
            zope_conf_additional = options.get('zope-conf-additional', '')
        
            base_dir = self.buildout['buildout']['directory']
        
            z_log_name = options.get('zeo-log', os.path.sep.join(('var', 'log', self.name + '.log',)))
            z_log = os.path.join(base_dir, z_log_name)
            z_log_dir = os.path.dirname(z_log)
            if not os.path.exists(z_log_dir):
                os.makedirs(z_log_dir)
            
            file_storage = options.get('file-storage', os.path.sep.join(('var', 'filestorage', 'Data.fs',)))
            file_storage = os.path.join(base_dir, file_storage)
            file_storage_dir = os.path.dirname(file_storage)
            if not os.path.exists(file_storage_dir):
                os.makedirs(file_storage_dir)
            
            zope_conf = zope_conf_template % dict(instance_home = instance_home,
                                                  z_log = z_log,
                                                  file_storage = file_storage,
                                                  zeo_address = zeo_address,
                                                  zope_conf_additional = zope_conf_additional,)
        
        zope_conf_path = os.path.join(location, 'etc', 'zeo.conf')
        open(zope_conf_path, 'w').write(zope_conf)
        
    def patch_binaries(self, ws_locations):
        location = self.options['location']
        # XXX We need to patch the windows specific batch scripts
        # and they need a different path seperator
        path =":".join(ws_locations)
        for script_name in ('runzeo', 'zeoctl'):
            script_path = os.path.join(location, 'bin', script_name)
            script = open(script_path).read()
            script = script.replace(
                '$SOFTWARE_HOME:$PYTHONPATH',
                '$SOFTWARE_HOME:'+path+':$PYTHONPATH'
                )
            f = open(script_path, 'w')
            f.write(script)
            f.close()

    def install_scripts(self, ws_locations):
        options = self.options
        location = options['location']
        
        zeo_conf = options.get('zeo-conf', None)
        
        zeo_conf = os.path.join(location, 'etc', 'zeo.conf')
        extra_paths = [os.path.join(location),
                       os.path.join(options['zope2-location'], 'lib', 'python')
                      ]
        extra_paths.extend(ws_locations)
        
        requirements, ws = self.egg.working_set(['plone.recipe.zope2zeoserver'])

        zc.buildout.easy_install.scripts(
            [(self.name, 'plone.recipe.zope2zeoserver.ctl', 'main')],
            ws, options['executable'], options['bin-directory'],
            extra_paths = extra_paths,
            arguments = ('\n        ["-C", %r]'
                         '\n        + sys.argv[1:]'
                         % zeo_conf
                         ),
            )


# The template used to build zeo.conf
zope_conf_template="""\
%%define INSTANCE %(instance_home)s

<zeo>
  address %(zeo_address)s
  read-only false
  invalidation-queue-size 100
</zeo>

<filestorage 1>
  path %(file_storage)s
</filestorage>

<eventlog>
  level info
  <logfile>
    path %(z_log)s
    format %%(message)s
  </logfile>
</eventlog>

<runner>
  program $INSTANCE/bin/runzeo
  socket-name $INSTANCE/etc/zeo.zdsock
  daemon true
  forever false
  backoff-limit 10
  exit-codes 0, 2
  directory $INSTANCE
  default-to-interactive true
  # user zope
  #python /usr/bin/python2.4
  #zdrun /opt/Zope-2.9.0/lib/python/zdaemon/zdrun.py

  # This logfile should match the one in the zeo.conf file.
  # It is used by zdctl's logtail command, zdrun/zdctl doesn't write it.
  logfile %(z_log)s
</runner>

%(zope_conf_additional)s
"""