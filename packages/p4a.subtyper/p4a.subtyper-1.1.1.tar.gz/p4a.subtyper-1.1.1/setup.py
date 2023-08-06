from setuptools import setup, find_packages

version = '1.1.1'

readme = open('README.txt')
long_description = readme.read()
readme.close()

setup(name='p4a.subtyper',
      version=version,
      description="Subtyping framework for Plone",
      long_description=long_description,
      classifiers=[
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Rocky Burt',
      author_email='rocky@serverzen.com',
      url='http://www.plone4artists.org/svn/projects/p4a.subtyper/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['p4a'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'p4a.z2utils'
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
