from setuptools import setup, find_packages

setup(
    name='ReprapAddOn',
    version='0.0.1',
    description='a simple addOn test',
    author='Mark "ckaos" Moissette',
    author_email='kaosat.dev@gmail.com',
    url='http://github.com/kaosat-dev/Doboz',
    keywords='web remote control remote monitoring reprap repstrap',
    license='GPL',
    classifiers=[
        "Development Status :: 1 - Planning",
        "Topic :: Utilities",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.6"
    ], 
    packages =find_packages('.')
   # package_dir = {'':'reprap'}
    )