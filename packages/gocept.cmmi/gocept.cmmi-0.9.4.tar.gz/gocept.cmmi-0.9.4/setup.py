from setuptools import setup, find_packages

name = "gocept.cmmi"
setup(
    name = name,
    version = "0.9.4",
    author = "Thomas Lotze",
    author_email = "tl@gocept.com",
    description = \
    "**Deprecated** zc.buildout recipe for building a software package from source.",
    long_description = open("README.txt").read(),
    license = "ZPL 2.1",
    keywords = "buildout",
    classifiers = ["Framework :: Buildout"],
    url = "http://svn.gocept.com/repos/gocept/buildout-recipes/" + name,
    packages = find_packages("src"),
    include_package_data = True,
    package_dir = {"": "src"},
    namespace_packages = ["gocept"],
    install_requires = ["setuptools",
                        "zc.buildout",
                        "gocept.download",
                        ],
    entry_points = {"zc.buildout": ["default = %s:Recipe" % name,
                                    ],
                    },
    )
