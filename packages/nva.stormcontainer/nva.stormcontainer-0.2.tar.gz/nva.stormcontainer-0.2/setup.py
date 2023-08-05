from setuptools import setup, find_packages

version = '0.2'

long_description = "A Zope container for Storm" 

setup(name='nva.stormcontainer',
      version=version,
      description="A Zope Storm Container",
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='Storm Zope',
      author="'Christian Klinger'",
      author_email='cklinger@novareto.de',
      url='http://www.novareto.de',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['nva'],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'storm',
                        'ZODB3',
                        'zope.component',
                        'zope.interface',
                        'zope.schema',
                        'zope.app.testing',
                        'zope.app.component',
                        'zope.app.keyreference',
                        'zope.app.container',
                        'zope.app.pagetemplate',
                        'pysqlite',
                       ],      
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
