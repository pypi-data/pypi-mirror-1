from setuptools import setup, find_packages

version = '0.1b1'
readme = open("README.txt").read()

setup(name='iqpp.plone.rotating',
      version=version,
      description="Rotating content for Plone",
      long_description=readme[readme.find('Overview'):],
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='plone rotating random',
      author='Kai Diefenbach',
      author_email='kai.diefenbach@iqpp.de',
      url='http://www.iqpp.de',
      download_url = 'http://cheeseshop.python.org/pypi/iqpp.plone.rotating/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['iqpp', 'iqpp.plone'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
