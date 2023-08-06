# -*- coding: UTF-8 -*-

from setuptools import setup, find_packages

setup(
    name = 'TurboJson',
    version = '1.1.4',
    description = 'Python template plugin that supports JSON',
    author = 'Elvelind Grandin',
    author_email = 'elvelind+turbogears@gmail.com',
    maintainer = 'TurboGears project',
    maintainer_email = 'turbogears@googlegroups.com',
    url = 'http://docs.turbogears.org/TurboJson',
    download_url = 'http://pypi.python.org/pypi/TurboJson',
    license = 'MIT',
    keywords = [
        'python.templating.engines',
        'turbogears'
    ],
    install_requires = [
        'DecoratorTools >= 1.4',
        'RuleDispatch >= 0.5a0.dev-r2303',
        'simplejson >= 1.3'
    ],
    zip_safe = False,
    packages = find_packages(),
    classifiers = [
        'Development Status :: 5 - Production/Stable',
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
