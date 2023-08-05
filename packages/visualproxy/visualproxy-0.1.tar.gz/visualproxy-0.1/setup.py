from setuptools import setup, find_packages
setup(
    name = "visualproxy",
    version = "0.1",
    packages = find_packages(),
    install_requires = ['zope.interface >= 3.3.1'],
    extras_require = {
       'PyGTK': ['PyGTK >= 2.10.0'],
    },
    # metadata for upload to PyPI
    author = "Johan Dahlin",
    author_email = "jdahlin@async.com.br",
    description = "VisualProxy for Python",
    license = "GPL",
    keywords = "visualproxy proxy mvc user interface pygtk gtk",
    url = "http://code.launchpad.net/visualproxy/",
)
