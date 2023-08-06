try:
    from setuptools import setup, find_packages
except ImportError:
    import ez_setup
    ez_setup.use_setuptools()
    from setuptools import setup, find_packages

from setuptools import setup, find_packages
setup(
    name='mako-version-tag',
    version='1.0',
    author='Owen Jacobson',
    author_email='owen.jacobson@grimoire.ca',
    description='Displays pkg_resources distribution versions in Mako templates',
    url='http://alchemy.grimoire.ca/python/sites/mako-version-tag/',
    download_url='http://alchemy.grimoire.ca/python/releases/mako-version-tag/',

    long_description="""This library makes it very easy to include version information
in your mako templates. For example, displaying the current version in the footer for
each page makes keeping track of which version of the site is live on an environment
very straightforward.

To use this library, import it into your Mako templates, then call the ``distribution``
tag ::

    <%namespace name="v" module="versiontag"/>
    <!-- ... -->
    ${v.distribution('my-app')}
""",

    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],

    package_dir = {
        '':'src',
        'test':'.'
    },
    py_modules = ['versiontag'],

    setup_requires=[
        'Sphinx',
        'pkginfo'
    ],
    tests_require=[
        'nose >= 0.10.4',
        'mock >= 0.5.0'
    ],
    install_requires=[
        'setuptools'
    ],

    test_suite = 'nose.collector'
)
