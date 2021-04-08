from setuptools import setup

setup(
    name='rofi-rbw',
    version='0.3.0',
    description='Rofi frontend for Bitwarden',
    author='fdw',
    author_email='5821180+fdw@users.noreply.github.com',
    url='https://github.com/fdw/rofi-rbw',
    keywords='rofi bitwarden rbw',
    license='MIT',
    classifiers=[
        'License :: OSI Approved :: MIT License'
    ],

    packages=['rofi_rbw'],
    entry_points={
        'console_scripts': [
            'rofi-rbw = rofi_rbw.rofi_rbw:main'
        ]
    },
    install_requires=[
        'ConfigArgParse>0.15,<2.0.0'
    ]
)
