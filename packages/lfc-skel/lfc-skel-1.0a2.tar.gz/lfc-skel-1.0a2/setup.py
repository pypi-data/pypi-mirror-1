from setuptools import setup, find_packages
import os

version = '1.0a2'

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()

setup(name='lfc-skel',
      version=version,
      description="Paster templates for django-lfc",
      long_description=README,
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Development Status :: 4 - Beta",
        "Environment :: Plugins",
        "Framework :: Paste",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Framework :: Django",
        ],
      keywords='django django-lfc cms paster',
      author='Kai Diefenbach',
      author_email='kai.diefenbach@iqpp.de',
      url='http://www.iqpp.de',
      license='BSD',
      packages=find_packages(exclude=['ez_setup']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'PasteScript>=1.3',
          'Cheetah',
      ],
      entry_points="""
      [paste.paster_create_template]
      lfc_app=lfc_skel.pastertemplates:LFCAppTemplate
      """,
      )
