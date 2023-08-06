from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='BurnerOnFire',
      version=version,
      description="BurnerOnFire is multi-threaded program that can write same" + \
        " content (iso files for now) to multiple CD/DVD burners simultaneously.",
      long_description="""More information at http://www.kiberpipa.org/burneronfire/""",
      classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: X11 Applications :: GTK',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
      ],
      keywords='cd dvd burn burner pygtk',
      author=u'Domen Kozar',
      author_email='domen@dev.si',
      url='http://www.kiberpipa.org/burneronfire/',
      license='BSD',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      package_data={'burneronfire': ['icons/*.png', 'LICENSE.txt']},
      zip_safe=False,
      install_requires=[
        "minihallib",
      ],
      entry_points="""
      [console_scripts]
      burneronfire = burneronfire:main
      """,
      )
