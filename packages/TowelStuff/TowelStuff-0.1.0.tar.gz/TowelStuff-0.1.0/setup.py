from distutils.core import setup

setup(
    name='TowelStuff',
    version='0.1.0',
    author='John M. Gabriele',
    author_email='jmg3000@gmail.com',
    packages=['towel_stuff', 'towel_stuff.test'],
    scripts=['bin/stowe-towels.py', 'bin/wash-towels.py'],
    url='http://pypi.python.org/pypi/TowelStuff/',
    license='LICENSE.txt',
    description='Stuff you might use that involves your towel.',
    long_description=open('README.txt').read(),
)
