from distutils.core import setup

setup(
    name = "hakmatak",
    version = "1.0.0",
    author = "http://hakmatak.org/john",
    author_email = "http://hakmatak.org/john",
    url = "http://hakmatak.org",
    description = "A Webification (w10n) application.",
    long_description = "Hakmatak implements w10n specification.\nIt makes inner components of a data store directly addressable and accessible\nvia well-defined and meaningful URLs.",
    classifiers = [
        "Programming Language :: Python",
        #"Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
    #packages = [
    #    "hakmatak",
    #    "hakmatak.store",
    #    "hakmatak.store.read",
    #    "hakmatak.store.read.example",
    #    "hakmatak.store.write",
    #    "hakmatak.output",
    #    "hakmatak.cli",
    #    "hakmatak.wsgi",
    #],
    ##requires = ["ctypes","wsgiref.handlers"],
    #scripts = [
    #    "hakmatak/cli/hakmatakread",
    #    "hakmatak/cli/hakmatakwrite",
    #],
)
