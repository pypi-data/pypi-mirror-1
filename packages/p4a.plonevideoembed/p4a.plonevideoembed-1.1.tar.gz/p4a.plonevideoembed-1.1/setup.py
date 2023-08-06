from setuptools import setup, find_packages

version = '1.1'

setup(name='p4a.plonevideoembed',
      version=version,
      description="Plone4Artists video embedding add-on for Plone",
      long_description="""p4a.plonevideo is a video embedding add-on for the Plone
CMS.""",
      classifiers=[
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Plone Foundation',
      author_email='plone-developers@lists.sourceforge.net',
      url='http://svn.plone.org/svn/plone/plone.example',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['p4a'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'p4a.video>=1.0',
          'p4a.videoembed>=1.0',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
