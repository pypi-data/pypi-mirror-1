from setuptools import setup, find_packages
import os

version = '1.0.1'

setup(name='collective.synchro',
      version=version,
      description="synchronize content between plone instance",
      long_description=open(os.path.join("collective","synchro","README.txt")).read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='synchronisation export import plone',
      author='Ingeniweb',
      author_email='support@ingeniweb.com',
      url='https://svn.plone.org/svn/collective/collective.synchro',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points= {"console_scripts": [
            "synchronize_queue = collective.synchro.scripts:synchro_queues",
            "create_queue = collective.synchro.scripts:create_queue",
            "import_queue = collective.synchro.scripts:import_queue",
            ]
        },

      )
