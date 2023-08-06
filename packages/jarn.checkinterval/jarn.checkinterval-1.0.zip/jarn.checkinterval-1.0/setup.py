from setuptools import setup, find_packages

version = '1.0'

setup(name='jarn.checkinterval',
      version=version,
      description='Compute optimal interpreter check interval for Zope',
      long_description=open('README.txt').read() + '\n' +
                       open('CHANGES.txt').read(),
      classifiers=[
          'Framework :: Plone',
          'Framework :: Zope2',
          'Programming Language :: Python',
      ],
      keywords='python zope interpreter check interval',
      author='Jarn AS',
      author_email='info@jarn.com',
      url='http://www.jarn.com/',
      license='BSD',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['jarn'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
      ],
      entry_points={
          'console_scripts': 'checkinterval=jarn.checkinterval.checkinterval:main',
      },
)
