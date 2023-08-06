from setuptools import setup

version = '1.2.1'

long_description = '\n\n'.join([
    open('README.txt').read(),
    open('TODO.txt').read(),
    open('CHANGES.txt').read(),
    ])

tests_require = [
    'z3c.testsetup>=0.3',
    'zope.testing',
    ]

setup(name='sdistmaker',
      version=version,
      description="Make sdists tarballs for projects in svn tree",
      long_description=long_description,
      # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[],
      keywords=[],
      author='Reinout van Rees',
      author_email='reinout@vanrees.org',
      url='http://bitbucket.org/reinout/sdistmaker/',
      license='BSD',
      packages=['sdistmaker'],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'tha.tagfinder',
                        ],
      extras_require = {'test': tests_require},
      tests_require=tests_require,
      entry_points={
          'console_scripts': [
              'make_sdist = sdistmaker.maker:main',
              'sdists_from_tags = sdistmaker.iterator:main',
          ]},
      )
