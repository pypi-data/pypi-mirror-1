from distutils.core import setup
setup(name = 'pydt',
    description = "utilities for managing numerical data files",
    version = '0.1.0',
    author = "Angel Yanguas-Gil",
    author_email = "angel.yanguas@gmail.com",
    download_url = (
        "https://netfiles.uiuc.edu/ayg/www/stuff/pydt-0.1.0.tar.gz"),
    packages = ['dtt'],
    scripts = ['scripts/pydt'],
    classifiers = ["Development Status :: 2 - Pre-Alpha",
        "Environment :: Console",
        "Topic :: Scientific/Engineering",
        "Topic :: Utilities"]
)

