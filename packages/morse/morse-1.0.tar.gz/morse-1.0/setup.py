from setuptools import setup, find_packages

setup(
    name='morse',
    version='1.0',
    author='Augie Fackler <durin42@gmail.com>',
    py_modules=['morse'],
    description='Convert strings to morse code.',
    include_package_data = True,
    license="Apache License, Version 2.0",
    test_suite = "nose.collector",
    tests_require=['nose'],
    )
