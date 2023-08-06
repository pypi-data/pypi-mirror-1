#
try:
    import setuptools
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()

from setuptools import setup, Extension, find_packages

ext = Extension("_estraiernative",
                ["estraiernative.c"],
                libraries=["estraier"],
                include_dirs=["/usr/include/estraier", "/usr/include/qdbm"],
                )

setup(
        name="Hypy", 
        description='Pythonic wrapper for Hyper Estraier',
        author='Yusuke YOSHIDA',
        author_email='usk@nrgate.jp',
        maintainer='Cory Dodt',
        maintainer_email='pypi@spam.goonmill.org',
        url='http://goonmill.org/hypy/',
        download_url='http://hypy-source.goonmill.org/archive/tip.tar.gz',
        version="0.8.2", 
        ext_modules=[ext],
        zip_safe=False,
        packages=find_packages(),

        classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Environment :: Web Environment',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
          'Operating System :: POSIX',
          'Programming Language :: Python',
          'Topic :: Software Development :: Libraries',
          'Topic :: Internet :: WWW/HTTP :: Indexing/Search',
          ],
      )
