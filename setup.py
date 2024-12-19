from setuptools import setup, find_packages

setup(
    name="mise",
    version="0.0.1",
    description="A qualitative data analysis tool",
    author="Timothy Elder",
    author_email="timothy.b.elder@dartmouth.edu",
    url="https://github.com/timothyelder/mise",
    project_urls={
        "Bug Tracker": "https://github.com/timothyelder/mise/issues",
        "Documentation": "https://github.com/timothyelder/mise/wiki", 
    },
    packages=find_packages(),
    install_requires=[
        "PySide6==6.5.1",
        "python-docx>=0.8.11",
        "markdown",
        "json",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",  # Minimum Python version
)