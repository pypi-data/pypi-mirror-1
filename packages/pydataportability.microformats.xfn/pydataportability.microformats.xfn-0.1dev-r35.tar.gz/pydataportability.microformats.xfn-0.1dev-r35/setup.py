from setuptools import setup, find_packages

version = '0.1'

setup(name='pydataportability.microformats.xfn',
      version=version,
      description="an XFN parser for the microformats package",
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
      keywords='microformats dataportability xfn parser web',
      author='Christian Scholz',
      author_email='cs@comlounge.net',
      url='http://mrtopf.de/blog',
      license='LGPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['pydataportability','pydataportability.microformats'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'pydataportability.microformats.base',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
