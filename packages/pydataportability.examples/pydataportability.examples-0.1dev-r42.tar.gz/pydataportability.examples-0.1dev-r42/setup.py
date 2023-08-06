from setuptools import setup, find_packages

version = '0.1'

setup(name='pydataportability.examples',
      version=version,
      description="Examples of how to use the pydataportability libraries",
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
      keywords='python dataportability examples',
      author='Christian Scholz',
      author_email='cs@comlounge.net',
      url='http://mrtopf.de/blog',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['pydataportability'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'pydataportability.microformats.base',
          'pydataportability.microformats.hcard',
          'pydataportability.microformats.xfn',
          'pydataportability.xrds',
      ],
      entry_points={
        'console_scripts': [
            'mf_etree = pydataportability.examples.scripts.twitter:main',
            'mf_bsoup = pydataportability.examples.scripts.twitter2:main',
            'xrds = pydataportability.examples.scripts.xrds:main',
        ],
      },
      )
