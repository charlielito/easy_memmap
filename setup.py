from setuptools import setup, find_packages
     

with open("README.md", "r") as readme:
    setup(
        name = "easy_memmap",
        version = "0.0.2",
        author = "Carlos Alvarez",
        author_email = "candres.alv@gmail.com",
        description = "Easy memmap",
        long_description = readme.read(),
        license = "MIT",
        keywords = [],
        url = "https://github.com/charlielito/easy_memmap",
        packages = find_packages(),
        package_data={},
        include_package_data = True,
        install_requires = ['numpy']
    )
