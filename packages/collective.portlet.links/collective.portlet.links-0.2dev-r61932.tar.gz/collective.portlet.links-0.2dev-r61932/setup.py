from setuptools import setup, find_packages

version = '0.2'

setup(name='collective.portlet.links',
      version=version,
      description="A Plone portlet with configureable links.",
      long_description="""\
This is a plone 3.x portlet offering configureabe links. On demand you can 
configure an additional CSS class on the a-tag.
""",
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Jan Filip Tristan Hasecke',
      author_email='blenderkid@web.de',
      url='',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective.portlet'],
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
