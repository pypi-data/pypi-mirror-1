from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='HTConsole',
      version=version,
      description="A web-based Python console",
      long_description="""\
An interactive, explorative Python console available as a web page.

This project explores the idea of representing Python objects as live
HTML/HTTP objects.

Also available in a `Subversion repository
<http://svn.pythonpaste.org/Paste/apps/HTConsole/trunk#egg=HTConsole-dev>`_
""",
      classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Framework :: Paste",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development",
        ],
      keywords='python console web paste',
      author='Ian Bicking',
      author_email='ianb@colorstudy.com',
      #url='',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'PasteDeploy',
          'Wareweb',
          'simplejson',
          'RuleDispatch',
          'WebHelpers',
          'Paste',
      ],
      entry_points="""
      [paste.app_factory]
      main = htconsole.wsgiapp:make_app

      [console_scripts]
      htconsole = htconsole.command:main
      """,
      )
      
