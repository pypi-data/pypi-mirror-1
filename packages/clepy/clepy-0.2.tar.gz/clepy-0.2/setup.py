from setuptools import setup

setup(

    name="clepy",
    version="0.2",
    packages=["clepy"],

    install_requires=[
        'processing >= 0.52',
        'decorator >= 3.0',
    ],

    url="http://code.google.com/p/clepy",
    license="MIT License",
    description="utilities from the Cleveland Python user group", 
    maintainer="W. Matthew Wilson",
    maintainer_email="matt@tplus1.com",
)

