from setuptools import setup, find_packages
import os

version = '1.0.2'

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
    name = 'kss.plugin.jsmath',
    version = version,
    description = "KSS jsMath plugin",
    long_description = long_description,
    author = "KissBooth collective",
    #author_email = "",
    url = "http://kssproject.org",
    license = 'GPL v3',
    install_requires = ["kss.core>=1.2"],
    packages = find_packages(),
    include_package_data = True,
    zip_safe = False,
    test_suite = 'kss.plugin.jsmath.tests.test_suite',
    entry_points = {
        'kss.plugin': [
            # Will be needed for the next kss version.
            ##'sdnd=ksspluginjsmath.config:Ksspluginjsmath'
            ],
        },
)
