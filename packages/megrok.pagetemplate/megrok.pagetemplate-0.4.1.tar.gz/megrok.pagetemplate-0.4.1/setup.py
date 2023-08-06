from setuptools import setup, find_packages
import os

version = '0.4.1'

setup(name='megrok.pagetemplate',
      version=version,
      description=("Page template component for Grok, "
                   "based on zope.pagetemplate"),
      long_description = u"%s\n\n%s" % (
          open(os.path.join("src", "megrok", "pagetemplate", "README.txt"
                            )).read(),
          open(os.path.join("docs", "HISTORY.txt")).read()
          ),
      classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Zope3',
        'Intended Audience :: Other Audience',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        ],
      keywords='Grok Pagetemplate Zope Layout Dolmen',
      author='Souheil Chelfouh',
      author_email='trollfot@gmail.com',
      url='http://pypi.python.org/pypi/megrok.pagetemplate',
      license='GPL',
      packages=find_packages('src', exclude=['ez_setup']),
      package_dir={'': 'src'},
      namespace_packages=['megrok'],
      include_package_data=True,
      zip_safe=False,
      platforms = 'Any',
      extras_require={'test': [
          'zope.browserpage',
          'zope.container',
          'zope.interface',
          'zope.site',
          'zope.testing',
          'zope.traversing',
          ]},
      install_requires=[
          'grokcore.component',
          'grokcore.view>=1.12.2',
          'grokcore.viewlet',
          'martian',
          'setuptools',
          'zope.component >= 3.9.1',
          'zope.pagetemplate',
          'zope.publisher',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
