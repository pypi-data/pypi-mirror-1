from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='mr.parker',
      version=version,
      description="Ensures that the PyPI bus factor for a package is above a " \
                  "certain threshold.",
      long_description=open(os.path.join('src', 'mr', 'parker', 'README.txt')).read() + "\n",
      classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 3",
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Topic :: Software Development",
        "Topic :: System :: Software Distribution",
        "Topic :: Utilities",
        ],
      keywords='',
      author='Matthew Wilkes',
      author_email='matthew@matthewwilkes.co.uk',
      url='http://dev.plone.org/collective/browser/mr.parker',
      license='BSD',
      package_dir = {'':'src'},
      packages=find_packages('src', exclude=['ez_setup']),
      namespace_packages=[],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'Distribute',
      ],
      entry_points="""
      # -*- Entry points: -*-
      [console_scripts]
      parker = mr.parker:commandline
      """,
      )
