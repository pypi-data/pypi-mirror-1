import ez_setup
ez_setup.use_setuptools()
from setuptools import setup

setup(name="PDIS-XPath",
    version="0.3",
    description="Pure-Python XPath evaluator based on ElementTree",
    author="Ken Rimey",
    author_email="rimey@hiit.fi",
    url="http://pdis.hiit.fi/pdis/download/",
    license="MIT License",
    long_description="""This is a pure-Python XPath evaluator based on
        ElementTree. It supports a substantial fraction of the XPath 1.0
        specification, notwithstanding the limitation that only the self, 
        child, and attribute axes are supported. The parser underlying the 
        evaluator attempts to handle all of XPath 1.0. """,
    namespace_packages = ['pdis'],
    packages=[
        'pdis',
        'pdis.xpath',
        'pdis.xpath.tests',
    ],
    install_requires = ["elementtree"],
)
