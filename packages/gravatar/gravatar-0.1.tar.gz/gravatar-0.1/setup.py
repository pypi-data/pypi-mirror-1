from setuptools import setup, find_packages
setup(
    # Package metadata
    name = 'gravatar',
    version = '0.1',
    packages = find_packages(),
    description='Gravatar generator. Includes all API parameters included in their documentation.',
    license='2-clause BSD',
    keywords='Gravatar web avatar uri',

    # Test metadata
    test_suite='testAll.allTests',

    # Author metadata
    author='Jake Voytko',
    author_email='jakevoytko@gmail.com',
    url='http://github.com/jakevoytko/pyGravatar')
