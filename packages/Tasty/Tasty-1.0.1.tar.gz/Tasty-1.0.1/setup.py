from setuptools import setup, find_packages
from turbogears.finddata import find_package_data

classifiers = """\
Development Status :: 5 - Production/Stable
Environment :: Web Environment
Intended Audience :: Developers
License :: OSI Approved :: GNU General Public License (GPL)
Operating System :: OS Independent
Topic :: Internet :: WWW/HTTP
Topic :: Internet :: WWW/HTTP :: Dynamic Content 
"""

setup(
    name="Tasty",
    version="1.0.1",
    author="Anders Pearson",
    author_email="anders@columbia.edu",
    url="http://tasty.python-hosting.com/",
    install_requires = ["TurboGears >= 0.8a5","restresource >= 0.1"],
    description="rich, general purpose tagging engine built as a REST service",
    long_description="rich, general purpose tagging engine built as a REST service",
    scripts = ["tasty_start.py"],
    license = "http://www.gnu.org/licenses/gpl.html",
    platforms = ["any"],
    classifiers = filter(None, classifiers.split("\n")),    
    zip_safe=False,
    packages=find_packages(),
    package_data = find_package_data(where='tasty',
                                     package='tasty'),
    )
    

