from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='collective.funkbot',
      version=version,
      description="Using buildbot and funkload, allow you to have a feedback of your modifications of a python project with funkload differencial reports and buildbot waterfall",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='',
      author='JeanMichel FRANCOIS',
      author_email='jeanmichel.francois@makina-corpus.com',
      url='https://svn.plone.org/svn/collective/collective.funkbot',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'PasteScript'
          # -*- Extra requirements: -*-
      ],
      entry_points="""
         # -*- Entry points: -*-
         [paste.paster_create_template]
         funkbot = collective.funkbot.funkbot:Funkbot
      """,
      setup_requires=["PasteScript"],
      paster_plugins = ["ZopeSkel"],
      )
