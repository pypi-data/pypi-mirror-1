from setuptools import setup, find_packages

version = '1.0b1'

setup(name='simplon.plone.currency',
      version=version,
      description="Currency handling for Plone",
      long_description=open("README.txt").read(),
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP :: Site Management",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Site Management",
        ],
      keywords='',
      author='Wichert Akkerman',
      author_email='wichert@simplon.biz',
      url='https://code.simplon.biz/svn/zope/simplon.plone.currency/trunk',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['simplon'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          "plone.app.form"
      ],
      )
