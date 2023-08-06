from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='indra.ipc',
      version=version,
      description="Indra support libs for IPC",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='lindenlab secondlife indra virtualworlds',
      author='Linden Lab',
      author_email='info@lindenlab.com',
      url='http://wiki.secondlife.com/wiki',
      license='MIT License',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['indra'],
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
