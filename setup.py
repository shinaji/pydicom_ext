from setuptools import setup, find_packages
from pydicom_ext import __version__

REQUIRES = []
CLASSIFIERS = [
    "License :: OSI Approved :: MIT License",
    "Intended Audience :: Developers",
    "Intended Audience :: Healthcare Industry",
    "Intended Audience :: Science/Research",
    "Development Status :: 5 - Production/Stable",
    "Programming Language :: Python",
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 3.4",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python :: 3.6",
    "Operating System :: OS Independent",
    "Topic :: Scientific/Engineering :: Medical Science Apps.",
    "Topic :: Scientific/Engineering :: Physics",
    "Topic :: Software Development :: Libraries"]

setup(
    name='pydicom_ext',
    version=__version__,
    description='Get back the pydicom series read function which has been detached from pydicom repo',
    url='https://github.com/pydicom_ext/pydicom_ext',
    author='shinaji',
    author_email='shina.synergy@gmail.com',
    license='MIT',
    keywords='dicom python medical imaging',
    packages=find_packages(),
    install_requires=REQUIRES,
    classifiers=CLASSIFIERS,
)
