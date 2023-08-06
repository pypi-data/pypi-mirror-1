from distutils.core import setup, Extension

setup (name = "py3k_extension",
       version = "20081023",
       maintainer = "kai zhu",
       maintainer_email = "kaizhu256@gmail.com",
       description = "extension module backporting opcodes from python3k",
       ext_modules = [
  Extension("_py3k_extension", sources = ["_py3k_extension.c"])
  ],
       scripts = ["py3k_extension.py"],
)
