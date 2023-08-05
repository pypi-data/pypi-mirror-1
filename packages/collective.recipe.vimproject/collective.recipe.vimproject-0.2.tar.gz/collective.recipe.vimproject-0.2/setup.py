from setuptools import setup, find_packages

version = '0.2'
name = 'collective.recipe.vimproject'

setup(name=name,
      version=version,
      description="Set up a VIM development environment.",
      long_description=file("README.txt").read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Buildout",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Stefan Eletzhofer',
      author_email='stefan.eletzhofer@inquant.de',
      url='https://svn.plone.org/svn/collective/buildout/collective.recipe.vimproject/trunk',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective.recipe'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'mkvimproject',
          # -*- Extra requirements: -*-
      ],
      entry_points = {
          "zc.buildout": ["default = %s:Recipe" % name, ],
          },
      )
