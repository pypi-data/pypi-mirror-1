from setuptools import setup, find_packages

version = '1.0.2'
readme = open('README.txt')
long_description = readme.read()
readme.close()

setup(name='p4a.fileimage',
      version=version,
      description="File/Image widget for Zope 3",
      long_description=long_description,
      classifiers=[
          'Framework :: Zope3',
          'Programming Language :: Python',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Topic :: Software Development :: Libraries :: Python Modules',
          ],
      keywords='',
      author='Rocky Burt',
      author_email='rocky@serverzen.com',
      url="http://pypi.python.org/pypi/p4a.fileimage/",
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['p4a'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
