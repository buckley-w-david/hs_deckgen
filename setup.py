import setuptools


setuptools.setup(
    name='hs_markov',
    version='0.0.1',
    long_description='',
    author='David Buckley',
    url='https://github.com/buckley-w-david/hs_markov',
    packages=setuptools.find_packages('src'),
    package_dir={'': 'src'},
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Me',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
    ],
    entry_points='''
        [console_scripts]
        hsdeck=hs_markov.cli:main
    '''
)
