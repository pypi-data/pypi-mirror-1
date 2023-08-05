from setuptools import setup, find_packages

setup(
    name="TurboKid",
    version="0.9.9",
    description="Python template plugin that supports Kid templates",
    author="Kevin Dangoor",
    author_email="dangoor+turbogears@gmail.com",
    url="http://www.turbogears.org/docs/plugins/template.html",
    download_url="http://www.turbogears.org/download/",
    license="MIT",
    keywords=["python.templating.engines", "turbogears"],
    install_requires = ["kid >= 0.9.1"],
    zip_safe=False,
    packages=find_packages(),
    classifiers = [
        'Development Status :: 3 - Alpha',
        #'Environment :: TurboGears',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    entry_points="""
    [python.templating.engines]
    kid = turbokid.kidsupport:KidSupport
    """,
    test_suite = 'nose.collector',
    )
    
