from setuptools import setup, find_packages

setup(
    name="simtradinggame",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "streamlit",
        "pandas",
        "numpy",
        "PyGithub",
        "streamlit-autorefresh",
        "streamlit-code-editor",
    ],
    extras_require={
        "dev": [
            "pytest",
            "black",
            "flake8",
            "mypy",
        ]
    },
    python_requires=">=3.8",
    author="Original Author",
    description="A simulated trading game with bot support",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
) 