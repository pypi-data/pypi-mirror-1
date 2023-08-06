from setuptools import setup, find_packages

version = '0.1a3'

setup(name='plone.app.gloworm',
      version=version,
      description="A Firebug-like inspector tool for Plone.",
      long_description="""\
""",
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='WebLion Group, Penn State University',
      author_email='support@weblion.psu.edu',
      url='https://weblion.psu.edu/svn/weblion/weblion/plone.app.gloworm/',
      license='GPL',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      include_package_data=True,
      namespace_packages=['plone.app', 'plone'],
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
