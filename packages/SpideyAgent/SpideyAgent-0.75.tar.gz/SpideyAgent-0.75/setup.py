from setuptools import setup, find_packages
from turbogears.finddata import find_package_data

setup(
    name="SpideyAgent",
    version="0.75",
    description="Each user can run their own threaded search engine and contribute to a global search database searching only the sites they want",
    license= "GPL",
    author="Ben Hamilton",
    author_email="ben.hamilton@gmail.com",
    url="http://sourceforge.net/projects/pyspider",
    install_requires = ["TurboGears >= 0.9a1dev-r852"],
    scripts = ["start-spider.py"],
    zip_safe=False,
    packages=find_packages(),
    package_data = find_package_data(where='spider',
                                     package='spider'),
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    test_suite = 'nose.collector',
    )
    
