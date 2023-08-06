from setuptools import setup, find_packages

version = '0.2'

readme = open('README.txt')
long_description = readme.read()
readme.close()

setup(name='p4a.image',
      version=version,
      description="",
      long_description=long_description,
      classifiers=[], # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='David Siedband',
      author_email='technique@oceanicsky.com',
      url='http://svn.plone.org/svn/plone/plone.example',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['p4a'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          'p4a.subtyper',
          'p4a.z2utils',
          'p4a.fileimage',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
