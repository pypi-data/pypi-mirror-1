import sys
try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

version = '0.1.1'

setup(
    name = "SQLiteFKTG4SA",
    version = version,
    description = "SQLite Foreign Key Trigger Generator for SQLAlchemy",
    author = "Randy Syring",
    author_email = "randy@rcs-comp.com",
    url='http://code.google.com/p/sqlitefktg4sa/',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
      ],
    license='BSD',
    packages=['sqlitefktg4sa'],
    install_requires = [
        "sqlalchemy",
    ],
    extras_require = {
        'testing':  ['Elixir>=0.6.1']
    },
    zip_safe=True
)