import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="async-cache",
    version="1.9.9",
    author="UT1C",
    author_email="liteman1000@gmail.com",
    description="An asyncio Cache",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/UT1C/async-cache",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
    keywords=["asyncio", "lru", "cache", "async", "cache", "lru-cache", "ttl"],
)
