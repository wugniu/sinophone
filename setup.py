import os.path

from setuptools import find_packages, setup

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()


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
    return get_variable("sinophone/__init__.py", f"__{magic_var_name}__")


setup(
    name="sinophone",
    version=get_magic_variable_from_init_py("version"),
    description="Python package for manipulating Chinese phonology.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author=get_magic_variable_from_init_py("author"),
    author_email=get_magic_variable_from_init_py("email"),
    url="https://github.com/wugniu/sinophone",
    license=get_magic_variable_from_init_py("license"),
    packages=[p for p in find_packages() if p.startswith("sinophone")],
    install_requires=[
        "ipapy==0.0.9",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
