from setuptools import setup

setup(
    name="ACFJ-waterdrop",
    version="1.0",
    py_modules=["waterdrop"],
    include_package_data=True,
    install_requires=["click"],
    entry_points="""
        [console_scripts]
        waterdrop=waterdrop:cli
    """,
)
