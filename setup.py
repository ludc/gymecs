from setuptools import find_packages, setup


with open("requirements.txt") as f:
    reqs = [line.strip() for line in f]

setup(
    name="gymecs",
    version="0.01",
    python_requires=">=3.7",
    packages=find_packages(),
    install_requires=reqs,
)
