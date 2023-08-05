from setuptools import setup, find_packages

setup(
    name="TurboJson",
    version="1.1",
    description="Python template plugin that supports json ",
    author="Elvelind Grandin",
    author_email="elvelind+turbogears@gmail.com",
    url="http://www.turbogears.org/docs/plugins/template.html",
    download_url="http://www.turbogears.org/download/",
    license="MIT",
    keywords=["python.templating.engines", "turbogears"],
    install_requires=["RuleDispatch"],
    zip_safe=False,
    packages=find_packages(),
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Framework :: TurboGears',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    entry_points="""
    [python.templating.engines]
    json = turbojson.jsonsupport:JsonSupport
    """,
    test_suite = 'nose.collector',
    )
    
