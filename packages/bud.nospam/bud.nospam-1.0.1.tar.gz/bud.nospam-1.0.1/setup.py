from setuptools import setup, find_packages

setup(
    name='bud.nospam',
    version='1.0.1',
    description="ROT 13 encrypt text to prevent spam",
    long_description=open("README.txt").read() + "\n" +
                   open("CHANGES.txt").read(),
    classifiers=[
    "Programming Language :: Python",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: Text Processing :: Markup :: HTML",
    ],
    keywords='web spam',
    author='Kevin Teague',
    author_email='kevin@bud.ca',
    license='BSD',
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    namespace_packages=['bud'],
    install_requires=[
      'setuptools',
    ],
    include_package_data=True,
    zip_safe=False,
)
