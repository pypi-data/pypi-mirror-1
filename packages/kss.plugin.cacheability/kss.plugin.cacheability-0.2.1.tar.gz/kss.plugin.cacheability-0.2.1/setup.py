from setuptools import setup, find_packages
import os

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = read('kss', 'plugin', 'cacheability', 'version.txt').strip()

long_description = (
        read('docs', 'README.txt')
        + '\n' +
        read('docs', 'INSTALL.txt')
        + '\n' +
        read('docs', 'HISTORY.txt')
        + '\n'
        )

setup(
    name = 'kss.plugin.cacheability',
    version = version,
    description = "KSS transitional cacheability plugin",
    long_description = long_description,
    author = "KissBooth collective",
    author_email = "info@zestsoftware.nl",
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
