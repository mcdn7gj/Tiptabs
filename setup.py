from setuptools import setup

setup(
    name="tiptabs",
    version="1.0.0",
    packages=["Tiptabs"],
    install_requires=[
        "Flask>=3.1.3,<4",
        "requests>=2.32.5,<3",
        "python-dotenv>=1.2.1,<2",
        "gunicorn>=19.9.0",
    ],
    url="https://github.com/mcdonagj/Tiptabs",
    license="MIT",
    author="Gary McDonald",
    entry_points={
        'console_scripts': ['tiptabs = Tiptabs.main:main'],
    },
)
