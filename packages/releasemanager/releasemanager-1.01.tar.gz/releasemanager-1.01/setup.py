import ez_setup
ez_setup.use_setuptools()
from setuptools import setup, find_packages

import os
execfile(os.path.join("src", "release.py"))

setup(
    name="releasemanager",
    version=version,
    
    # uncomment the following lines if you fill them out in release.py
    description=description,
    author=author,
    author_email=email,
    url=url,
    download_url=download_url,
    license=license,
    
    install_requires = [
        "Amara >= 1.2", 
        "SQLAlchemy >= 0.3",
    ],
    entry_points = """
    [console_scripts]
    relman_ctl = releasemanager.utils.relman_ctl:main
    [releasemanager.web]
    """,
    zip_safe=False,
    package_dir={'' : 'src'},
    packages=find_packages('src'),
    include_package_data = True,
    package_data = {
      '' : ['*.txt', '*.xml'],
    },
    namespace_packages=['releasemanager'],
    keywords = [
        "release", "software deployment", "distributed environment",
    ],
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
    ],
)
    
