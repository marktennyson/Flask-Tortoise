from setuptools import setup,find_packages


VERSION_INFO = (0, 0, 1)
AUTHOR = "Aniket Sarkar"

with open("README.md", "r") as f:
    long_description = f.read()

def get_install_requires() -> list:
    with open("requirements.txt", "r") as f:
        return [line.rstrip() for line in f]


setup(
    name="Flask-Tortoise",
    version=".".join([str(v) for v in list(VERSION_INFO)]),
    url="https://github.com/marktennyson/flask-tortoise",
    license="GNU General Public License v3 or later (GPLv3+)",
    author=AUTHOR,
    author_email="aniketsarkar@yahoo.com",
    description="Adds Tortoise ORM support for flask app.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords=["flask", "flask-tortoise", "Tortoise"],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    platforms="any",
    install_requires=get_install_requires(),
    extras_require={},
    python_requires=">=3.6,<4",

    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Flask",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)