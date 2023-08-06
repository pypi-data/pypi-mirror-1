
import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, find_packages

setup(
    name='$package_name',
    version='0.0.0',
    description='A new haus application.',
    packages=find_packages(),
    install_requires="haus",
    include_package_data=True,
)

