from setuptools import setup, find_packages

version = '1.0'

setup(name='qi.Goban',
      version=version,
      description="A product for storing, viewing and annotating Go game records in plone.",
      long_description="""\
qi.Goban is a product for Go players and clubs. It allows you to add games as content, view them, comment on them, and add variations.
Features:
 * Import games from the standard go format sgf version 4
 * Display ajax views of the game (using kss)
 * Supports full annotations, letters, triangles, etc.
 * Parse and add variations to games
 * Export pdf diagrams (using sgf2dg)
 * Automatic tagging according to the rank of the players
""",
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='plone go games',
      author='G. Gozadinos',
      author_email='ggozad@qiweb.net',
      url='http://svn.plone.org/svn/collective/qi.Goban',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['qi'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
