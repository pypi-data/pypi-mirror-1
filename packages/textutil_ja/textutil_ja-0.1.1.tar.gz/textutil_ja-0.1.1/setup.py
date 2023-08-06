from setuptools import setup, find_packages
import sys, os

version = '0.1.1'

setup(name='textutil_ja',
      version=version,
      description="textutil_ja - helpers for handling japanese text",
      long_description="""\
textutil_ja is helper library for handling japanese text.
""",
      classifiers=filter(None, map(str.strip, """\
Development Status :: 3 - Alpha
License :: OSI Approved :: MIT License
Programming Language :: Python
""".splitlines())),
      keywords='',
      author='Chihio Sakatoku',
      author_email='csakatoku@gmail.com',
      url='http://code.google.com/p/textutil_ja/',
      license='MIT License',
      platforms=['any'],
      packages=find_packages(exclude=['ez_setup', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      test_suite='nose.collector'
      )
