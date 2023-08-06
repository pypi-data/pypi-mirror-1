from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='megrok.pagetemplate',
      version=version,
      description=("Page template component for Grok, "
                   "based on zope.pagetemplate"),
      long_description = (
          open("src/megrok/pagetemplate/README.txt").read() + "\n" +
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
      install_requires=[
          'setuptools',
          'grokcore.view',
          'grokcore.viewlet',
          'grokcore.component',
          'zope.pagetemplate'
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
