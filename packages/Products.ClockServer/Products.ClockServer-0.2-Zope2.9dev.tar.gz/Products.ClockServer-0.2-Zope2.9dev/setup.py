from setuptools import setup, find_packages

version = '0.2-Zope2.9'

setup(name='Products.ClockServer',
      version=version,
      description="The Zope ClockServer product provides a mechanism for users to call Zope object methods without the use of an external clock source (e.g. cron/wget).",
      long_description="""\
The Zope ClockServer product provides a mechanism for users to call Zope object methods without the use of an external clock source (e.g. cron/wget). It operates by acting as a medusa "server", essentially coopting Zope's asyncore mainloop and injecting "fake" requests into Zope's ZPublisher. Despite the complicated description, it's rather easy to use.""",
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Chris McDonough',
      author_email='chrism@plope.com',
      maintainer='Roberto Allende',
      maintainer_email='rover@menttes.com',
      url='http://labs.menttes.com/zope/products/clockserver',
      license='ZPL 2.1',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
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
