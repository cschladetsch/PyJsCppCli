from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ai-cli",
    version="0.2.0",
    author="AI CLI Developer",
    author_email="example@example.com",
    description="A command-line interface for AI models",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/ai-cli",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "anthropic>=0.44.0",
        "prompt_toolkit>=3.0.39",
        "pyperclip>=1.8.2",
    ],
    entry_points={
        "console_scripts": [
            "ai=ai.cli:main",
        ],
    },
)
