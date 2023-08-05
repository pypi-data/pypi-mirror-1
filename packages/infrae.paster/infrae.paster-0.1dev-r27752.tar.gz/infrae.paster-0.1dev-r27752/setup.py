from setuptools import setup, find_packages

name = "infrae.paster"
version = '0.1'

setup(name=name,
      version=version,
      description="Buildout recipe to create a part using a paster template",
      long_description=open("README.txt").read(),
      classifiers=[
        "Framework :: Buildout",
        "Framework :: Paste",
        "License :: OSI Approved :: Zope Public License"
        ], 
      keywords='buildout recipe paster',
      author='Sylvain Viollon',
      author_email='info@infrae.com',
      url='https://svn.infrae.com/buildout/infrae.paster',
      license='ZPL 2.1',
      packages=find_packages(),
      namespace_packages = ['infrae'],
      install_requires = ['zc.buildout', 'setuptools', 'paste', 'ZopeSkel'],
      entry_points = {
        'zc.buildout': ['default = %s:Recipe' % name],
        },
      include_package_data=True,
      zip_safe=True,
      )

