from distutils.core import setup

setup(
    name = "archiwe",
    version = "0.9.0",
    author = "http://hakmatak.org/dev",
    author_email = "dev@hakmatak.org",
    url = "http://pypi.python.org/pypi/archiwe",
    description = "Webification of archive files",
    long_description = "Archiwe webifies files in archive formats such as zip, tar, etc. It is based on hakmatak, the w10n enabler.",
    classifiers = [
        "Programming Language :: Python",
        #"Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
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
        "archiwe",
        #"archiwe/cli",
        "archiwe/store",
        "archiwe/store/write",
        "archiwe/store/read",
        #"archiwe/wsgi",
    ],
    #requires = ["ctypes","wsgiref.handlers"],
    scripts = [
        "archiwe/cli/archiweread",
        "archiwe/cli/archiwewrite",
    ],
)
