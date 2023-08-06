from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='affinitic.docpyflakes',
      version=version,
      description="Pyflakes your doctest",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development",
        "Topic :: Utilities",
        "Programming Language :: Python"],
      keywords='',
      author='Affinitic',
      author_email='jfroche@affinitic.be',
      url='http://svn.affinitic.be/python/affinitic.docpyflakes',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['affinitic'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'pyflakes'],
      entry_points={
        'console_scripts': ['docpyflakes = affinitic.docpyflakes.docpyflakes:main']})
