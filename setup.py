import setuptools

with open("README.md", mode="r") as readme_file:
    long_description = readme_file.read()

with open("requirements.txt", mode="r") as requirements_file:
    requirements = [requirement.replace('\n', '') for requirement in requirements_file.readlines()]

setuptools.setup(
    name="ProjFormatter",
    version='0.0.1',
    description="A .*proj file formatter",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/SlimeStick/ProjFormatter",
    author="David Khitrik",
    packages=setuptools.find_packages(),
    python_requires=">=3.8",
    install_requires=requirements
)
