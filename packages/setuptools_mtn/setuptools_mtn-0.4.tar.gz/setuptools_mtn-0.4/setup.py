import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, find_packages

setup(
    name = "setuptools_mtn",
    version = "0.4",

    author = "Dale Sedivec",
    author_email = "dale@codefu.org",
    description = "setuptools support for discovering files kept in Monotone",
    license = "GPL",
    keywords = "setuptools monotone mtn",
    url = "http://www.codefu.org/setuptools_mtn/",

    py_modules = ["setuptools_mtn"],

    tests_require = [
        "nose",
        ],

    entry_points = {
        "setuptools.file_finders": [
            "mtn = setuptools_mtn:find_files_in_mtn"
            ],
        },
    )
