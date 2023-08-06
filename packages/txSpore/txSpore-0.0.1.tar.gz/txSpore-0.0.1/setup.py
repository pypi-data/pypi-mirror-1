from setuptools import setup

from txspore import meta


setup(
    name=meta.display_name,
    version=meta.version,
    description=meta.description,
    author=meta.author,
    author_email=meta.author_email,
    url=meta.url,
    license=meta.license,
    packages=[
        meta.library_name,
        "%s.original" % meta.library_name,
        "%s.testing" % meta.library_name,
        "%s.tests" % meta.library_name,
        "%s.url" % meta.library_name,
        ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        ],
    )
