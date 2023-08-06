from setuptools import setup, find_packages
import os.path

version = '1.1'

long_description = '\n\n'.join([
    open('README.txt').read(),
    open(os.path.join('src', 'tha', 'sdistmaker', 'USAGE.txt')).read(),
    open('TODO.txt').read(),
    open('CHANGES.txt').read(),
    ])

tests_require = [
    'z3c.testsetup>=0.3',
    'zope.testing',
    ]

setup(name='tha.sdistmaker',
      version=version,
      description="Make sdists tarballs for projects in svn tree",
      long_description=long_description,
      # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[],
      keywords=[],
      author='The Health Agency',
      author_email='techniek@thehealthagency.com',
      url='http://www.thehealthagency.com',
      license='BSD',
      package_dir={'': 'src'},
      packages=find_packages('src'),
      namespace_packages=['tha'],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'tha.tagfinder',
                        ],
      extras_require = {'test': tests_require},
      tests_require=tests_require,
      entry_points={
          'console_scripts': [
              'make_sdist = tha.sdistmaker.maker:main',
              'sdists_from_tags = tha.sdistmaker.iterator:main',
          ]},
      )
