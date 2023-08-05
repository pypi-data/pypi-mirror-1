import os
from setuptools import setup, find_packages

version = '0.1.0'
long_desc = open(os.path.join(os.path.dirname(__file__), 'README.txt')).read()

setup(name='haufe.releaser',
      version=version,
      description="Performs local upload of distribution files to a haufe.eggserver instance",
      long_description=long_desc,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Andreas Jung',
      author_email='andreas.jung@haufe.de',
      url='',
      license='ZPL V2.1',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['haufe'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""

      [distutils.commands]
      local_upload = haufe.releaser.commands:local_upload
      """
      )
