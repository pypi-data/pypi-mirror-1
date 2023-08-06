

from setuptools import setup, find_packages
setup(
    name="SizeDupe Reporter",
    version="0.9.1",
    author = "Joe Koberg",
    author_email = "joe@osoft.us",
    description = "File/directory size/duplicate scanning and reporting tool.",
    long_description = open('sizedupe/README.TXT').read(),
    license = "GPLv3",
    keywords = "space free disk filelight philesight dupe duplicate",
    packages = ['sizedupe'],
    package_data = {
        '': ['*.TXT', '*.txt'],
        },
    include_package_data = True,
    entry_points = {
        'console_scripts': [
            'sizedupe = sizedupe:main',
            ],
        },
    extras_require = {
        'PDF':  ["ReportLab>=2.0"],
        },
    )
    
