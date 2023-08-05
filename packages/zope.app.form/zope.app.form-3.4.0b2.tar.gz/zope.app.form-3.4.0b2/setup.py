from setuptools import setup, find_packages

setup(name='zope.app.form',
      version = '3.4.0b2',
      url='http://svn.zope.org/zope.app.form',
      author='Zope Corporation and Contributors',
      author_email='zope3-dev@zope.org',

      packages=find_packages("src"),
      package_dir={"": "src"},

      namespace_packages=["zope", "zope.app"],
      include_package_data=True,
      install_requires=[
          "setuptools",
          "ZODB3",
          "zope.app.container",
          "zope.app.publisher",
          "zope.cachedescriptors",
          "zope.component",
          "zope.configuration",
          "zope.deprecation",
          "zope.exceptions",
          "zope.i18n",
          "zope.interface",
          "zope.proxy",
          "zope.publisher",
          "zope.schema",
          "zope.security",
          "zope.app.basicskin",
          "zope.location>=3.4.0a1-1",
          ],
      extras_require={"test": ['zope.app.testing',
                               'zope.app.securitypolicy',
                               'zope.app.zcmlfiles']},
      zip_safe=False,
      )

