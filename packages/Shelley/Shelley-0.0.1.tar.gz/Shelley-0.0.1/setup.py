from setuptools import setup
 
setup(
    name='Shelley',
    version='0.0.1',
    description='Simple map drawing',
    author='Graham Carlyle',
    author_email='graham@grahamcarlyle.com',
    packages=['shelley', 
              'shelley.apps.web',
              'shelley.datasources', 
              'shelley.renderers',
              'shelley.mappers',
              'shelley.mappers.mapnik'],
    install_requires=['setuptools', 'pyproj'],
    extras_require={
        'gdal': ['GDAL'],
        'geodjango': ['django'],
        'tests': ['GDAL', 'django', 'minimock', 'psycopg2']
    },
    url='http://pypi.python.org/pypi/Shelley',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering :: GIS'
    ],
)
