
from distutils.core import setup
from distutils.extension import Extension

Import = Extension(name="cimport",
                      sources=["cimport.c"])
Html = Extension(name="_c_htmltext",
                      sources=["_c_htmltext.c"])

setup(name = "cimport",
      version = "0.1",
      description = "Import tools for Python",
      author = "Neil Schemenauer",
      author_email = "nas@mems-exchange.org",
      ext_modules = [Import, Html]
      )
