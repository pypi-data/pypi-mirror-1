from setuptools import setup, find_packages
import os

version = '0.1.0'

setup(name='collective.flowplayer_toolbar',
      version=version,
      description="A Plone module which an accessible Javascript toolbar to collective.flowplayer",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='plone flowplayer javascript player toolbar accessibility',
      author='RedTurtle Technology',
      author_email='luca.fabbri@redturtle.net',
      url='http://svn.plone.org/svn/collective/collective.flowplayer_toolbar/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'collective.flowplayer>3.0dev',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      setup_requires=["PasteScript"],
      paster_plugins = ["ZopeSkel"],
      )
