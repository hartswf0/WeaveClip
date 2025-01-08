from setuptools import setup, find_packages

setup(
    name="weaveclip",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'PyQt6',
        'pytest'
    ],
)
