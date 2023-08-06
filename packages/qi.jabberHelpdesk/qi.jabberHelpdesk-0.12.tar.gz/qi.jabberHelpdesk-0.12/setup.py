from setuptools import setup, find_packages

version = '0.12'

setup(name='qi.jabberHelpdesk',
      version=version,
      description="An online helpdesk product for plone",
      long_description="""\
A plone product that enables online customer support using jabber""",
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='plone jabber helpdesk',
      author='G. Gozadinos',
      author_email='ggozad@qiweb.net',
      url='http://chatblox.com',
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
