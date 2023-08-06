from setuptools import setup

setup(
    name='NoseMultiVersion',
    version="0.1",
    author="Kumar McMillan",
    author_email="kumar.mcmillan@gmail.com",
    maintainer="Kumar McMillan",
    maintainer_email="kumar.mcmillan@gmail.com",
    description="A Nose plugin to run tests simultaneously in different versions of Python.",
    long_description=open('./README.rst').read(),
    url='',
    license='MIT License',
    entry_points = {
        'nose.plugins.0.10': [ 
            'multiversion = nosemultiversion:MultiVersion',
            'multiversion_worker = nosemultiversion:MultiVersionWorker']
        },
    py_modules = ['nosemultiversion'],
    install_requires = ['nose>=0.11.1', 'execnet']
    )
