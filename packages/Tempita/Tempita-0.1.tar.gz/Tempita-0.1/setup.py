from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='Tempita',
      version=version,
      description="A very small text templating language",
      long_description="""\
Tempita is a small templating language for text substitution.

This isn't meant to be the Next Big Thing in templating; it's just a
handy little templating language for when your project outgrows
``string.Template`` or ``%`` substitution.  It's small, it embeds
Python in strings, and it doesn't do much else.

You can read about the `language
<file:///home/ianb/src/Tempita/docs/html/#the-language>`_, the
`interface <file:///home/ianb/src/Tempita/docs/html/#the-interface>`_,
and there's nothing more to learn about it.

0.1 is the initial release.
""",
      classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Topic :: Text Processing',
      ],
      keywords='templating template language html',
      author='Ian Bicking',
      author_email='ianb@colorstudy.com',
      url='http://pythonpaste.org/tempita/',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
      ],
      entry_points="""
      """,
      )
