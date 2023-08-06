try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

from smarthttp.__init__ import __version__ as VERSION


setup(
    name='SmartHTTP',
    version=VERSION,
    description='Smart HTTP handling module with support for popular site engines.',
    author='Dan Kluev',
    author_email='dan@kluev.name',
    install_requires=["pycurl", "lxml", "demjson", "sqlalchemy", "paste"],

    packages=find_packages(),
    data_files=[('smarthttp', ['smarthttp/ua.txt']),
                ('smarthttp/lang', ['smarthttp/lang/unicode_blocks.txt', 'smarthttp/lang/translit.txt'])],
    include_package_data=True,
    zip_safe=False,
    test_suite='nose.collector',
    entry_points="""
    """,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)

