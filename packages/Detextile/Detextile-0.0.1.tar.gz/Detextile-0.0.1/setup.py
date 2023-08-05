"""Convert HTML to Textile syntax using BeautifulSoup."""

import ez_setup
ez_setup.use_setuptools()
from setuptools import setup, find_packages

doclines = __doc__.split("\n")

setup(
      name = "Detextile",
      version = "0.0.1",
      packages = find_packages(),

      author = "Roberto De Almeida",
      author_email = "roberto@dealmeida.net",
      description = doclines[0],
      #long_description = "\n".join(doclines[2:]),
      license = "MIT",
      keywords = "textile html",
      #url = "http://example.com/HelloWorld/", 
     )
