from distutils.core import setup

setup(
    name = "hakmatak",
    version = "1.1.1",
    author = "http://hakmatak.org/dev",
    author_email = "dev@hakmatak.org",
    url = "http://hakmatak.org",
    description = "A webification (w10n) service enabler",
    long_description = "Hakmatak implements the w10n specification. It is used to create WSGI applications that RESTfully expose complex data stores.",
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
    packages = [
        "hakmatak",
        "hakmatak/cli",
        "hakmatak/output/html",
        "hakmatak/output",
        "hakmatak/store",
        "hakmatak/store/write",
        "hakmatak/store/read",
        "hakmatak/store/read/example",
        "hakmatak/util",
        "hakmatak/wsgi",
    ],
    #requires = ["ctypes","wsgiref.handlers"],
    scripts = [
        "hakmatak/cli/hakmatakread",
        "hakmatak/cli/hakmatakwrite",
    ],
)
