from setuptools import setup, find_packages

version = '1.0'

long_description = '\n\n'.join([open('README.txt').read(),
                                open('CHANGES.txt').read()])

setup(name='eolfixer',
      version=version,
      description="Reinout's installable copy of pypy's fixeol script",
      long_description=long_description,
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python',
          'Topic :: Software Development :: Quality Assurance',
          'Topic :: Utilities'],
      keywords='',
      author='Reinout van Rees',
      author_email='reinout@vanrees.org',
      url='http://bitbucket.org/reinout/eolfixer',
      license='MIT',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=[],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'py',
      ],
      entry_points={
          'console_scripts': [
              'eolfixer = fixeol:main',
              ],
          },
      )
