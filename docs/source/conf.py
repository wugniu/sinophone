# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys


def read(rel_path: str):
    here = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(here, rel_path), "r", encoding="utf-8") as fp:
        return fp.read()


def get_variable(rel_path: str, var_name: str):
    for line in read(rel_path).splitlines():
        if line.startswith(var_name):
            delim = '"'  # if '"' in line else "'"
            return line.split(delim)[1]


def get_magic_variable_from_init_py(magic_var_name: str):
    return get_variable(
        os.path.abspath("../../sinophone/__init__.py"), f"__{magic_var_name}__"
    )


# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
sys.path.insert(0, os.path.abspath(".."))
sys.path.insert(0, os.path.abspath('../..'))
sys.path.insert(1, os.path.abspath("../sinophone"))

print(sys.path)
print(get_magic_variable_from_init_py("version"))


# -- Project information -----------------------------------------------------

project = "sinophone"
copyright = "Copyright (c) 2022 Yuanhao Chen"
author = get_magic_variable_from_init_py("author")

# The full version, including alpha/beta/rc tags
release = get_magic_variable_from_init_py("version")


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = ["sphinx.ext.autodoc"]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]
