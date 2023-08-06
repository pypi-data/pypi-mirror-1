import setuptools

setuptools.setup(
    name='python-at',
    version='0.1',
    author='Eddy Mulyono',
    author_email='eddymul@gmail.com',
    license='BSD',
    description='Pythonic wrapper around command-line `at`',
    packages=setuptools.find_packages(exclude='at.tests'),
    test_suite='at.tests',
    )
