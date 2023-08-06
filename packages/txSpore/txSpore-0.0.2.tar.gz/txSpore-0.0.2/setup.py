from setuptools import setup

from txspore import meta
from txspore.util import dist


setup(
    name=meta.display_name,
    version=meta.version,
    description=meta.description,
    author=meta.author,
    author_email=meta.author_email,
    url=meta.url,
    license=meta.license,
    packages=dist.findPackages(meta.library_name),
    long_description=dist.catReST(
        "docs/PRELUDE.txt",
        "README",
        "docs/INSTALL.txt",
        "docs/USAGE.txt",
        "docs/API.txt",
        "TODO",
        "docs/HISTORY.txt",
        stop_on_errors=True,
        out=True),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        ],
    )
