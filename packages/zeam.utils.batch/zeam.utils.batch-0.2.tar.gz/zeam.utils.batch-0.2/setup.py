from setuptools import setup, find_packages
import os

version = '0.2'

setup(name='zeam.utils.batch',
      version=version,
      description="Generic Batch support for Zope",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: BSD License",
        ],
      keywords='batch zope',
      author='Sylvain Viollon',
      author_email='thefunny@gmail.com',
      url='',
      license='BSD',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['zeam', 'zeam.utils'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
         'setuptools',
	 'zope.interface',
	 'zope.schema',
	 'zope.annotation',
	 'zope.traversing',
	 'zope.app.pagetemplate',
	 'zope.cachedescriptors',
	 'zope.testing',
	 ],
      )
