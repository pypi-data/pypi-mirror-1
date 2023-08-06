from setuptools import setup, find_packages
from os.path import join

readme = open('README.txt').read()
history = open(join('docs', 'HISTORY.txt')).read()

setup(name = 'example.blobattype',
      version = '1.0b2',
      description = 'Example of migrating an AT-based content type using blob-enabled FileFields.',
      long_description = readme[readme.find('\n\n'):] + '\n' + history,
      classifiers = [
        'Environment :: Web Environment',
        'Framework :: Plone',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
      ],
      keywords = 'plone blobs archetypes content example',
      author = 'George Gozadinos',
      author_email = 'ggozad@qiweb.net',
      url = 'http://pypi.python.org/pypi/example.blobattype',
      license = 'GPL',
      packages = find_packages('src'), 
      package_dir = {'': 'src'},
      namespace_packages = ['example'],
      include_package_data = True,
      platforms = 'Any',
      zip_safe = False,
      install_requires = ['setuptools'],
      entry_points = """
        [z3c.autoinclude.plugin]
        target = plone
      """,
)
