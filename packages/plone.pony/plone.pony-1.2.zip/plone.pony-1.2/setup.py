from setuptools import setup, find_packages
from os.path import join

name = 'plone.pony'
version = '1.2'
readme = open("README.txt").read()
history = open(join('docs', 'HISTORY.txt')).read()

setup(name = name,
      version = version,
      description = 'A pony for Plone.',
      long_description = readme[readme.find('\n\n'):] + '\n' + history,
      classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Plone',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Other Audience',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
      ],
      keywords = 'plone pony',
      author = 'Plone Foundation',
      author_email = 'plone-developers@lists.sourceforge.net',
      url = 'http://svn.plone.org/svn/plone/plone.pony',
      download_url = 'http://cheeseshop.python.org/pypi/plone.pony/',
      license = 'GPL',
      packages = find_packages(exclude=['ez_setup']),
      namespace_packages = ['plone'],
      include_package_data = True,
      platforms = 'Any',
      zip_safe = False,
      install_requires=[
          'setuptools',
      ],
      entry_points = '',
)

