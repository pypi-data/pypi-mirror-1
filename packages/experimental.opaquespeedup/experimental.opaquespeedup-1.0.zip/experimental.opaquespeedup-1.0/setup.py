from setuptools import setup, find_packages
from os.path import join

name = 'experimental.opaquespeedup'
version = '1.0'
readme = open("README.txt").read()
history = open(join('docs', 'HISTORY.txt')).read()

setup(name = name,
      version = version,
      description = 'Plone-specific optimization of looking up CMF\'s "opaque items"',
      long_description = readme[readme.find('\n\n'):] + '\n' + history,
      classifiers = [
        'Environment :: Web Environment',
        'Framework :: Plone',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Other Audience',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
      ],
      keywords = 'plone events opaque optimization',
      author = 'Jarn AS',
      author_email = 'info@jarn.com',
      url = 'http://www.jarn.com/',
      download_url = 'http://pypi.python.org/pypi/%s/' % name,
      license = 'GPL',
      packages = find_packages(exclude=['ez_setup']),
      namespace_packages = ['experimental'],
      include_package_data = True,
      platforms = 'Any',
      zip_safe = False,
      install_requires = ['setuptools',],
)

