from setuptools import setup

setup(
    name='arise-protoype',
    version='0.0.1',
    packages=['arise_prototype'],
    install_requires=['pandas',
                      'numpy',
                      'datetime',
                      'djangorestframework',
                      'django-cors-headers']
)
