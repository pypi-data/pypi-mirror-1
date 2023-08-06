from setuptools import setup, find_packages

version = '1.0'

setup(
    name='bud.nospam',
    version=version,
    description="ROT 13 encrypt text to prevent spam",
    long_description=open("README.txt").read() + "\n" +
                   open("HISTORY.txt").read(),
    classifiers=[
    "Programming Language :: Python",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: Text Processing :: Markup :: HTML",
    ],
    keywords='web spam',
    author='Kevin Teague',
    author_email='kevin@bud.ca',
    license='BSD',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['bud'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
      'setuptools',
    ],
)
