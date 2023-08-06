from setuptools import setup, find_packages
setup(
    name="defaultencodinghack",
    version="0.2",
    include_package_data=True,
    zip_safe=False,
    author='Laurence Rowe',
    author_email='laurence@lrowe.co.uk',
    description='"Sometimes digging a hole is fast, but you will fall into it later on and pay the price" -- anonymous',
    long_description=open('README.txt').read(),
    license='BSD',
    packages=find_packages(),
    )
