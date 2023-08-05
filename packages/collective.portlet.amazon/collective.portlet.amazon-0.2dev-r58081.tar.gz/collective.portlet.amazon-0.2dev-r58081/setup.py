from setuptools import setup, find_packages

version = '0.2'

setup(name='collective.portlet.amazon',
      version=version,
      description="This ifor Plone 3 that allows you to display a product from Amazon.com and make money through your Amazon Affiliates account.",
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
      keywords='web zope plone portlet amazon',
      author='Jonathan Wilde',
      author_email='plone-developers@lists.sourceforge.net',
      url='http://www.speedbreeze.com',
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
