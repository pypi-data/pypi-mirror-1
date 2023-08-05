from setuptools import setup, find_packages

version = '1.0'

setup(
    name = 'kss.plugin.livesearch',
    version = version,
    description = "KSS livesearch / autocomplete plugin",
    author = "KissBooth collective",
    #author_email = "",
    url = "http://kssproject.org",
    install_requires = [
        "kss.core",
        "setuptools",
        ],
    packages = find_packages(),
    include_package_data = True,
    namespace_packages = ['kss.plugin'],
    test_suite = 'kss.plugin.livesearch.tests.test_suite',
    entry_points = {
        'kss.plugin': [
            'livesearch=ksspluginlivesearch.config:Ksspluginlivesearch'
            ],
        },
)
