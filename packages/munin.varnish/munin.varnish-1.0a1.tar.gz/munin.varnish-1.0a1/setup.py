from setuptools import setup, find_packages
from os.path import join

version = '1.0a1'
readme = open("README.txt").read()
history = open(join('docs', 'HISTORY.txt')).read()

setup(name = 'munin.varnish',
      version = version,
      description = 'Munin plugins for Varnish.',
      long_description = readme[readme.find('\n\n'):] + '\n' + history,
      classifiers = [
          'Development Status :: 3 - Alpha',
          'Framework :: Buildout',
          'Intended Audience :: Developers',
          'Topic :: Software Development :: Build Tools',
          'Topic :: System :: Networking :: Monitoring',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          ],
      keywords = 'munin monitoring',
      author = 'Michael Dunstan',
      author_email = 'michael@elyt.com',
      url = 'http://pypi.python.org/pypi/munin.varnish',
      license = 'GPL',
      packages = find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages = ['munin'],
      include_package_data = True,
      platforms = 'Any',
      zip_safe = False,
      install_requires = [
          'setuptools',
          ],
      entry_points = {
          "zc.buildout": ["default = munin.varnish:Recipe"],
          },

)
