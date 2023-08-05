from setuptools import setup, find_packages

version = '0.1'

setup(name='bazaarrecipe',
      version=version,
      description="Buildout recipe for Bazaar",
      long_description="""
A buildout recipe which can be used to branch a Bazaar repository.
This makes it possible to automatically create branches for relevant
code.

Usage
=====

If you have a buildout config you can add a section like:

[sources]
recipe = bazaar
urls =
     http://bazaar-vcs.org/bzr/bzr.dev bzr.dev
     http://bazaar.launchpad.net/~bialix/heads/trunk heads

This will create a `sources` folder in you buildout root with two
subfolders in it (bzr.dev and heads).

Changes to you buildout configuration might trigger removal of the
sources dir. However, before this happens the recipe makes sure there
are no modifications left. If it sees any it will abort before
anything is deleted. This means you can safely use it for development.

Running buildout again after you have done a succesful build before
will do a bzr pull on each of the resources.
""",
      classifiers=[
        'Framework :: Buildout',
        'Topic :: Software Development :: Build Tools',
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: BSD License',
        ], 
      keywords='',
      author='Jeroen Vloothuis',
      author_email='jeroen.vloothuis@xs4all.nl',
      url='https://launchpad.net/bazaarrecipe',
      license='GPL',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      entry_points="""
      # -*- Entry points: -*-
      [zc.buildout]
      default = bazaarrecipe:Recipe

      [zc.buildout.uninstall]
      default = bazaarrecipe:uninstall
      """,
      )
