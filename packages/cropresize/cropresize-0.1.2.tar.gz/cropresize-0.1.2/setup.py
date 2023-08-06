from setuptools import setup, find_packages
import sys, os

version = '0.1.2'

setup(name='cropresize',
      version=version,
      description="crop and resize an image without doing the math yourself",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='image',
      author='Jeff Hammel',
      author_email='jhammel@openplans.org',
      url='http://pypi.python.org/pypi/cropresize',
      license='GPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
        'PIL',
        ],
      dependency_links=[
        "http://dist.repoze.org/PIL-1.1.6.tar.gz",
        ],
      entry_points="""
      # -*- Entry points: -*-
      [console_scripts]
      crop-resize = cropresize:main
      """,
      )
