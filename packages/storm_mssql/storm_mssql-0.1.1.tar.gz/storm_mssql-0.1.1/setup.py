from setuptools import setup, find_packages
setup(
    name = "storm_mssql",
    version = "0.1.1",
    package_dir={'' : 'src'},
    packages = find_packages('src'),
)
