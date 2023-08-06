from setuptools import setup, find_packages
import sys, os

version = '0.1.2'

setup(name='taras.recipe.distutils',
    version=version,
    description="Recipe for zc.buildout that downloads one or multiple distutils-archives and installs them without requiring for zc.distutils to be installed.",
    long_description="""\
""",
    classifiers=[
          'Development Status :: 3 - Alpha',
          'Environment :: Plugins',
          'Framework :: Buildout',
          'Intended Audience :: Developers',
          'Programming Language :: Python',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: System :: Installation/Setup',
          'License :: OSI Approved :: BSD License',
          ],
    keywords='distutils buildout',
    author='Taras Mankovski',
    author_email='tarasm@gmail.com',
    url='http://github.com/taras/taras.recipe.distutils',
    license='BSD License',
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    namespace_packages = ['taras', 'taras.recipe'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        # -*- Extra requirements: -*-
    ],
    entry_points={'zc.buildout':
      ['default = taras.recipe.distutils:Recipe']
      },
)
