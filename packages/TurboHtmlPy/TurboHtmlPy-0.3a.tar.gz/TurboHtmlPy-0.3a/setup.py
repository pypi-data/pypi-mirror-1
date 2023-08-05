from setuptools import setup, find_packages

#python ~/bin/soft-python/rst2html_plus/rst2html_plus.py turbohtmlpy/README.txt devdoc

setup (
    name = "TurboHtmlPy",
    version = "0.3a",
    description="Template plugin for TurboGears (?and Buffet?) using Formencode.htmlgen",
    author="David Bernard",
    author_email="dwayne@java-fan.com",
    url="http://dwayneb.free.fr/turbohtmlpy/",
    #download="http://dwayneb.free.fr/turbohtmlpy/TurboHtmlPy-0.1-py2.4.egg",
    license="LGPL",
    classifiers = [
    'Development Status :: 3 - Alpha',
    #'Environment :: TurboGears',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    
    
    install_requires = ["FormEncode >= 0.4"],
    #scripts = [],
    packages=find_packages(),
    zip_safe=False,
    entry_points="""
	[python.templating.engines]
	htmlpy = turbohtmlpy.templater:TurboHtmlPy
    """,
    test_suite = 'nose.collector',
)
    
