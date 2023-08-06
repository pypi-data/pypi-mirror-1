import os
from setuptools import setup, find_packages

version = '0.3b1'

def description():
    join = os.path.join
    return (open(join('docs', 'README.txt')).read() + '\n' +
            open(join('docs', 'HISTORY.txt')).read() + '\n')

setup(name='collective.dancing',
      version=version,
      description="The all-singing all-dancing newsletter product for Plone.",
      long_description=description(),

      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='zope plone notification newsletter',
      author='Daniel Nouri, Thomas Clement Mogensen and contributors',
      author_email='singing-dancing@googlegroups.com',
      url='http://plone.org/products/dancing',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,

      # If the dependency to z3c.form gives you trouble within a Zope
      # 2 environment, try the `fakezope2eggs` recipe
      install_requires=[
          'setuptools',
          'collective.singing',
          'five.intid',
          'plone.z3cform',
          'StoneageHTML',
      ],
      
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
