from setuptools import setup, find_packages
import os


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '0.1'

long_description = (
    read('README.txt')
    + '\n' +
    'Change history\n'
    '==============\n'
    + '\n' +
    read('CHANGES.txt')
    + '\n' +
    'Contributors\n'
    '============\n'
    + '\n' +
    read('CONTRIBUTORS.txt')
    + '\n' +
    'Download\n'
    '========\n\n'
    )

setup(name='vudo.skinsetup',
      version=version,
      description="Package which provides API and scripts to manage a skin directory of a VUDO app.",
      long_description=long_description,
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      keywords='wsgi web bfg repoze vudo',
      author='Stefan Eletzhofer',
      author_email='stefan.eletzhofer@inquant.de',
      url='git://github.com/reco/vudo.git',
      license='BSD',
      package_dir = {'': 'src'},
      packages=find_packages("src"),
      namespace_packages=['vudo'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      [console_scripts]
      vudoskin = vudo.skinsetup:main
      """,
      )
