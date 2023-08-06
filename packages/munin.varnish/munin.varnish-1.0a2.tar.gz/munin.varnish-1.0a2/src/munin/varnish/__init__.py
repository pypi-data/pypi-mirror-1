# -*- coding: utf-8 -*-
"""Recipe munin.varnish"""
import os
import shutil
import re
import stat


class Recipe(object):
    """zc.buildout recipe"""

    def __init__(self, buildout, name, options):
        self.buildout, self.name, self.options = buildout, name, options
        self.varnishstat = options['varnishstat']

    def install(self):
        """Installer"""

        # Copy script into place.
        src = os.path.join(os.path.dirname(__file__), 'varnish_')
        dst = os.path.join(
            self.buildout['buildout']['bin-directory'],
            self.name)
        shutil.copy(src, dst)
        os.chmod(dst,
                 stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH |
                 stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH |
                 stat.S_IWUSR )

        # Patch script.
        script = open(dst, 'r').read()
        expression = re.compile(r'^my \$varnishstatexec = .*$', re.MULTILINE)
        script = expression.sub('my $varnishstatexec = "%s";'
                                % self.varnishstat,
                                script)
        open(dst, 'w').write(script)

        # Return files that were created by the recipe. The buildout
        # will remove all returned files upon reinstall.
        return [dst]

    def update(self):
        """Updater"""
        pass
