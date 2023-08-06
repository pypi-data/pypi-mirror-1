# -*- coding: UTF-8 -*-

from setuptools import setup, find_packages

setup(
    name = 'TurboJson',
    version = '1.2',
    description = 'Python template plugin that supports JSON',
    author = 'Elvelind Grandin',
    author_email = 'elvelind+turbogears@gmail.com',
    maintainer = 'TurboGears project',
    maintainer_email =  'turbogears@googlegroups.com',
    url = 'http://docs.turbogears.org/TurboJson',
    download_url = 'http://pypi.python.org/pypi/TurboJson',
    license = 'MIT',
    keywords = [
        'python.templating.engines',
        'turbogears'
    ],
    install_requires = [
        'PEAK-Rules >= 0.5a1.dev-r2555',
        'simplejson >= 1.9.1'
    ],
    zip_safe = True,
    packages = find_packages(),
    classifiers = [
        'Development Status :: 4 - Beta',
        'Framework :: TurboGears',
        'Environment :: Web Environment :: Buffet',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    entry_points = """\
    [python.templating.engines]
    json = turbojson.jsonsupport:JsonSupport
    """,
    test_suite = 'nose.collector'
)
