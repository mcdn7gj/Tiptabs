from setuptools import setup

setup(
    name="tiptabs",
    version="1.0.0",
    packages=["Tiptabs"],
    install_requires=[
        "Flask>=0.12.3",
        "Flask-API>=0.7.1",
        "Jinja2>=2.9.6",
        "requests>=2.20.0",
        "MySQL-connector-python>=8.0.33",
        "python-dotenv>=0.10.1",
        "boto3>=1.9.119",
        "gunicorn>=19.9.0"
    ],
    url="https://github.com/mcdonagj/Tiptabs",
    license="MIT",
    author="Gary McDonald",
    entry_points={
        'console_scripts': ['tiptabs = Tiptabs.main:main'],
    },
)
