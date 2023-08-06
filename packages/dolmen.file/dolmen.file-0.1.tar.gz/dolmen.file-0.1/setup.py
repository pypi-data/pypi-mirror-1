from os.path import join
from setuptools import setup, find_packages

version = '0.1'

setup(name='dolmen.file',
      version=version,
      description="A Zope3/Grok File Representation package.",
      long_description= "%s\n\n%s" % (
          open(join('src', 'dolmen','file', 'README.txt')).read(),
          open(join('docs', 'HISTORY.txt')).read(),
          ),
      classifiers=[
          "Framework :: Zope3",
          "Programming Language :: Python",
          "Topic :: Software Development :: Libraries :: Python Modules",
          ],
      keywords='Grok Zope3 file download',
      author='Souheil Chelfouh',
      author_email='trollfot@gmail.com',
      url='',
      license='GPL',
      packages=find_packages('src', exclude=['ez_setup']),
      package_dir={'': 'src'},
      namespace_packages=['dolmen'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'grokcore.view',
          'zope.schema',
          'zope.security',
          'zope.interface',
          'zope.component',
          'zope.publisher',
          'zope.traversing',
          'zope.contenttype',
          'zope.app.file',
          'dolmen.builtins',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
