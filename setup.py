#!/usr/bin/env python3
"""
Setup script for Flashcard Generator
"""

from setuptools import setup, find_packages # type: ignore
from pathlib import Path

# Read README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text() if (this_directory / "README.md").exists() else ""

# Read requirements
requirements = []
requirements_file = this_directory / "requirements.txt"
if requirements_file.exists():
    with open(requirements_file) as f:
        requirements = [
            line.strip() 
            for line in f 
            if line.strip() and not line.startswith('#')
        ]

setup(
    name="flashcard-generator",
    version="1.0.0",
    author="Flashcard Generator Team",
    author_email="",
    description="An AI-powered application for generating flashcards from various input sources",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/flashcard-generator",  # Update with actual repo URL
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "flashcard-generator=flashcard_generator.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "flashcard_generator": ["config/*.json"],
    },
)
