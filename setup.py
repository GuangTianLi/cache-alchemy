"""The setup script."""

from setuptools import setup, find_packages

with open("README.rst") as readme_file:
    readme = readme_file.read()

with open("HISTORY.rst") as history_file:
    history = history_file.read()

requirements = ["configalchemy"]

setup_requirements = []

test_requirements = ["fakeredis"]


setup(
    author="GuangTian Li",
    author_email="guangtian_li@qq.com",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    description="The Python Cache Toolkit.",
    install_requires=requirements,
    long_description=readme + "\n\n" + history,
    include_package_data=True,
    keywords="cache-alchemy",
    name="cache-alchemy",
    packages=find_packages(include=["cache_alchemy*"]),
    setup_requires=setup_requirements,
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/GuangTianLi/cache-alchemy",
    version="0.1.3",
    zip_safe=False,
)
