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

import logging, os, re, shutil
from xml.sax.saxutils import quoteattr

import pkg_resources

import zc.buildout
import zc.recipe.egg

logger = logging.getLogger('gocept.zope3instance')


class Recipe:
    # Need to think about the inheritence interface
    # it *is* reasonable to think about instances as an
    # extension of the basic egg/script-generation model.

    def __init__(self, buildout, name, options):
        self.options = options
        self.name = name

        options['location'] = os.path.join(
            buildout['buildout']['parts-directory'],
            self.name,
            )

        skeletons = options.get('skeleton', name).split()
        options['skeleton'] = '\n'.join(
            os.path.join(buildout['buildout']['directory'], 'skels', name)
            for name in skeletons)

        if 'database-config' not in options:
            options['database-config'] = '\n'.join([
                buildout[section]['zconfig']
                for section in options['database'].split()
                ])

        options['bin-directory'] = buildout['buildout']['bin-directory']

        # Let the egg recipe do much of the heavy lifting.
        options['scripts'] = ''
        options.pop('entry-points', None)
        self.egg = zc.recipe.egg.Egg(buildout, name, options)

    def update(self):
        # For an update we remove the parts directory first,
        # and then re-create it.
        shutil.rmtree(self.options['location'])
        return self.install()

    def install(self):
        options = self.options
        destructible_paths = set()

        extra = options.get('extra-paths', '')
        options['extra-paths'] = extra

        # Compute various paths
        dest = options['location']
        zope_conf_path = os.path.join(dest, 'zope.conf')
        zdaemon_conf_path = os.path.join(dest, 'zdaemon.conf')

        for dir in ['log_dir', 'run_dir', 'subprogram_dir', 'config_dir']:
            if not options.has_key(dir):
                options[dir] = dest
            if not os.path.exists(options[dir]):
                make_tree_dir(options[dir])

        destructible_paths.add(options['subprogram_dir'])
        destructible_paths.add(options['config_dir'])

        options['site_zcml_path'] = os.path.join(options['config_dir'], 'site.zcml')

        if not os.path.exists(dest):
            os.mkdir(dest)
        destructible_paths.add(dest)

        requirements, ws = self.egg.working_set(['gocept.zope3instance'])

        # install subprograms and ctl scripts
        zc.buildout.easy_install.scripts(
            [('runzope', 'zope.app.server.main', 'main')],
            ws, options['executable'], options['subprogram_dir'],
            extra_paths = options['extra-paths'].split(),
            arguments = ('\n        ["-C", %r]'
                         '\n        + sys.argv[1:]'
                         % zope_conf_path),
            )

        # Install the scripts defined by this recipe, which adds entry points
        # missing from Zope itself.
        zc.buildout.easy_install.scripts(
            [('debugzope', 'gocept.zope3instance.zope3scripts', 'debug'),
             ('scriptzope', 'gocept.zope3instance.zope3scripts', 'script'),
             ],
            ws, options['executable'], options['subprogram_dir'],
            extra_paths = options['extra-paths'].split(),
            arguments = ('\n        ["-C", %r]'
                         '\n        + sys.argv[1:]'
                         % zope_conf_path),
            )

        zc.buildout.easy_install.scripts(
            [(self.name, 'gocept.zope3instance.ctl', 'main')],
            ws, options['executable'], options['bin-directory'],
            extra_paths = options['extra-paths'].split(),
            arguments = ('\n        %r,'
                         '\n        %r,'
                         '\n        ["-C", %r]'
                         '\n        + sys.argv[1:]'
                         % (os.path.join(options['subprogram_dir'], 'debugzope'),
                            os.path.join(options['subprogram_dir'], 'scriptzope'),
                            zdaemon_conf_path)
                         ),
            )

        self.installSkeleton(options['skeleton'].split(),
                             options['config_dir'],
                             options)
        destructible_paths.add(os.path.join(options['bin-directory'],
                                            self.name))
        return tuple(destructible_paths)


    def installSkeleton(self, sources, dest, options):
        """Installs ZCML and config files by using given skeletons
        and configuration data from buildout.

        """
        if not os.path.exists(dest):
            os.mkdir(dest)
        if not os.path.isdir(dest):
            raise Exception("%dest is not a directory.")

        sources = sources[:]
        sources.insert(0, os.path.join(os.path.dirname(__file__), 'skel'))
        # Copy skeletons
        for overlay in sources:
            if os.path.isdir(overlay):
                self._copy_skeleton(overlay, dest)

        self._update_infiles(dest, options)

    def _copy_skeleton(self, src, dest):
        """Copies a skeleton directory recursively."""
        # XXX Use pkg_resources to become zip_safe.
        for name in os.listdir(src):
            # Heuristic to avoid SCM files
            if name.startswith('.'):
                continue
            if name == 'CVS':
                continue
            src_name = os.path.join(src, name)
            if os.path.isdir(src_name):
                dest_name = os.path.join(dest, name)
                os.mkdir(dest_name)
                self._copy_skeleton(src_name, dest_name)
            else:
                shutil.copy(src_name, dest)

    def _update_infiles(self, dest, options):
        """Update a tree of files by converting .in files to
        their configured counterparts.

        """
        for name in os.listdir(dest):
            if name == '.svn':
                # ignore .svn directories
                continue
            in_file = os.path.join(dest, name)

            if os.path.isdir(in_file):
                # Recurse into directories
                return self._update_infiles(in_file, options)
            if not name.endswith('.in'):
                continue

            new_name = os.path.join(dest, name[:-3])
            if os.path.exists(new_name):
                raise zc.buildout.UserError("There are both %r and %r." % (
                    name, new_name))

            old_contents = file(in_file, 'r').read()
            new_contents = old_contents % options

            file(new_name, 'w').write(new_contents)
            os.remove(in_file)


def make_tree_dir(path):
    """Create a directory, even if that implies creating multiple levels of
    directories.
    """
    tail, head = os.path.split(path)
    if not os.path.exists(tail):
        make_tree_dir(tail)
    os.mkdir(path)
