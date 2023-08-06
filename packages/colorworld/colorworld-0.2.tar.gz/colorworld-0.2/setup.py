from setuptools import setup, find_packages
setup(
    name="colorworld",
    description="A module and python script to produce colored world maps "
    "from lists of data for countries.",
    url="http://tat.wright.name/colorworld/",

    version="0.2",
    author="Tom Wright",
    author_email="tat.wright@googlemail.com",
    license="BSD",
    keywords="chloropleth colorworld color world map svg",
    classifiers=[
        "Programming Language :: Python :: 2.5",
        "License :: OSI Approved :: BSD License",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Utilities",
    ],
    packages=['colorworld'],
    install_requires=['lxml'],
    entry_points={'console_scripts': ['color-world = colorworld.colorworld:main']},
    package_data={'colorword': ['*.csv', '*.svg']},

)
