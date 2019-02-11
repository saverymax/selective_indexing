import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
        name="SIS",
        version="0.1.1",
        author="Max Savery",
        author_email="savermax@gmail.com",
        description="Selective Indexing System (SIS) for classification of MEDLINE citations",
        long_description=long_description,
        long_description_content_type="text/markdown",
        url="https://github.com/saverymax/selective_indexing",
        packages=["SIS", "SIS.SIS_tests"],
        entry_points={
            'console_scripts': [
                "SIS=SIS.SIS:main"
                ]},
        classifiers=[
            "Programming Language :: Python :: 3.6",
            "Operating System :: Unix"
            ],
        install_requires=[
            "numpy>=1.14.3",
            "scipy>=1.1.0",
            "scikit-learn==0.20.2",
            "tensorflow==1.11.0",
            "Keras==2.2.4",
            "python-dateutil",
            "nltk"
            ],
        package_data={
            'SIS': [
                "./selectively_indexed_id_mapping.json",
                "./group_ids.json",
                "models/*",
                "SIS_tests/datasets/*"
                ]},
        )

