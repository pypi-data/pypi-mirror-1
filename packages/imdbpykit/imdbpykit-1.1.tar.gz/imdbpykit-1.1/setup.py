from setuptools import setup, find_packages
import sys, os

version = '1.1'

setup(
    name='imdbpykit',
    version=version,
    description="Web interface for IMDbPY",
    long_description="""IMDbPYKit is a web interface for IMDbPY using PasteWebkit.""",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Natural Language :: English",
        "Programming Language :: Python",
        "Operating System :: OS Independent",
        "Topic :: Database :: Front-Ends",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content :: CGI Tools/Libraries",
        ],
    keywords='imdb imdbpy paste webkit wsgi',
    author='H. Turgut Uyar',
    author_email='uyar@tekir.org',
    url='http://imdbpy.sourceforge.net/?page=programs#imdbpykit',
    license='GPL',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'PasteWebkit',
        'IMDbPY>4.0',
    ],
    entry_points="""
      # -*- Entry points: -*-
      [paste.app_factory]
      main = imdbpykit.wsgiapp:make_app
      """,
    )
