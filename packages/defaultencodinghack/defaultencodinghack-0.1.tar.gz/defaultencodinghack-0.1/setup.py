from setuptools import setup, find_packages
setup(
    name="defaultencodinghack",
    version="0.1",
    zip_safe=False,
    author='Laurence Rowe',
    author_email='laurence@lrowe.co.uk',
    description="Sets default encoding to utf8 in a hacky manner.",
    long_description=open('README.txt').read(),
    license='BSD',
    packages=find_packages(),
    )
