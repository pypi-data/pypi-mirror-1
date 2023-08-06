from distutils.core import setup

readme = open('README')
description = readme.read()
readme.close()

splitted = description.splitlines()
description = splitted[0]
long_description = '\n'.join(splitted[2:])

setup(
    name='webpage',
    version='0.1',
    description=description,
    long_description=long_description,
    author='Aristotelis Mikropoulos',
    author_email='amikrop@gmail.com',
    url='http://amikrop.gr/webpage.php',
    license='GPL',
    platforms=['OS Independent (Written in an interpreted language)'],
    py_modules=['webpage']
)
