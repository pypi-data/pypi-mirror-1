from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages
#
setup(name = "SimpleExampleEgg",
    version = "0.1",
    description = "test",
    author = "Todd Greenwood",
    author_email = "t.greenwoodgeer@gmail.com",
	entry_points = {'console_scripts': [
		'make_apple_pie = fruit.apple:doConsole'
		]},
    packages = find_packages(exclude=['ez_setup'] ),
	package_data = {'':['docs/*.html', 'docs/*.rest','docs/*.vim']},
    test_suite = 'fruit.simpletests.getTestSuite',
    license = "GNU Lesser General Public License",
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        "Programming Language :: Python",
        "Topic :: Utilities",
    ],
    zip_safe=True,
    )
