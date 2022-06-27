from setuptools import setup, find_packages

setup(
    name='game17',
    version='1.0',
    packages=find_packages(),
    include_package_data=False,
    install_requires=[
        'Click', 'numpy', 'pandas', 'matplotlib'
    ],
    entry_points='''
        [console_scripts]
        game17=game17.cli:cli
    '''
)
