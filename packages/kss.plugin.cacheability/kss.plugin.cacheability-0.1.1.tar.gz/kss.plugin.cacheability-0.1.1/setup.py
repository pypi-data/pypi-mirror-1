from setuptools import setup, find_packages
import os

version = '0.1.1'

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
        read('docs', 'README.txt')
        + '\n' +
#        'Recently changed\n'
#        '**********************\n'
#        + '\n' +
#        read('docs', 'NEWS.txt')
#        + '\n' +
        'Download\n'
        '**********************\n'
        )

setup(
    name = 'kss.plugin.cacheability',
    version = version,
    description = "KSS transitional cacheability plugin",
    long_description = long_description,
    author = "KissBooth collective",
    #author_email = "",
    url = "http://kssproject.org",
    license = 'GPL v3',
    install_requires = ["kss.core>=1.4"],
    zip_safe=False,
    packages = find_packages(),
    include_package_data = True,
    test_suite = 'kss.plugin.cacheability.tests.test_suite',
    entry_points = {
        'kss.plugin': [
            # needed for future dependency on kss.base
            ],
        },
)
