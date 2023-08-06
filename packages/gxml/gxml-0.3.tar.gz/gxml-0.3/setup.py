from setuptools import setup, find_packages
setup(
    name = "gxml",
    version = "0.3",
    packages = find_packages(),

    author = "Kenneth Miller",
    author_email = "xkenneth@gmail.com",
    keywords = "python xml elementtree lxml minidom xpath ironpython",
    url = "http://www.xkenneth.com/gxml",
    description = """A Good XML Abstraction. Provides a common interface to popular XML libaries. Currently supports elementree and minidom. Tutorials are available at www.xkenneth.com/gxml""",
)
