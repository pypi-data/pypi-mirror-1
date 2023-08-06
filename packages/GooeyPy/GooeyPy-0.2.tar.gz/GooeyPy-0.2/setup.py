from setuptools import setup, find_packages
import gooeypy

setup(
    name = "GooeyPy",
    version = gooeypy.__version__,
    url = gooeypy.__url__,
    packages = find_packages(),
    include_package_data = True,

    author = "Joey Marshall",
    author_email = "web@joey101.net",
    description = "A fast, flexible, and cool looking GUI for pygame.",
    license = "LGPL",
    keywords = "gooeypy gui pygame",
    platforms = 'any',
    long_description = gooeypy.__doc__,
    install_requires = ["Cellulose >= 0.2"]
)
