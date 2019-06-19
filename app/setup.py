from setuptools import setup

setup(
    name='opentrons_json_library',
    packages=['opentrons_json_library'],
    include_package_data=True,
    install_requires=[
        'flask',
    ],
)
