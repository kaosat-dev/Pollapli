from setuptools import setup, find_packages

setup(
    name='Hydroduino',
    version='0.0.1',
    description='hydroponics and gardening add on for Pollapli',
    author='Mark "ckaos" Moissette',
    author_email='kaosat.dev@gmail.com',
    url='http://github.com/kaosat-dev/Hydroduino',
    keywords='web remote control remote monitoring hydroponics gardens watering ',
    license='GPL',
    classifiers=[
        "Development Status :: 1 - Planning",
        "Topic :: Utilities",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.6"
    ], 
    packages =find_packages('.')
    )