from setuptools import setup, find_packages

version = '0.2'

setup(name='collective.portlet.rich',
      version=version,
      description="",
      long_description="""\
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
      author='Plone Foundation',
      author_email='pellekrogholt@gmail.com',
      url='http://plone.org',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', 'collective.portlet'],
      include_package_data=True,
      zip_safe=False,
      #TODO: set up a dependecy of the special plone.app.form branch that supports kupu/wysiwyg
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'collective.formlib.link',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
