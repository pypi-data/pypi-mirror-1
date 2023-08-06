from setuptools import setup, find_packages
import os

setup(name='collective.easyslider',
      version=open(os.path.join('collective', 'easyslider', 'version.txt')).read(),
      description="The product will allow you to apply an easyslider to any page with the ability to create each slide."
                  "It also provides a slider view for Folders and Collections.",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='plone easyslider',
      author='Nathan Van Gheem',
      author_email='vangheem@gmail.com',
      url='http://www.nathanvangheem.com/software/collective-easyslider',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
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
