from setuptools import setup, find_packages

version = '0.461'

setup(name="sqlbean",
        version=version,
        description="A auto maping orm .",
        long_description=""" """,
        author="zsp",
        author_email="zsp007@gmail.com",
        packages=find_packages(),
        install_requires=['dbutils', 'decorator'],
        zip_safe=False
)
