from setuptools import setup, find_packages
from turbogears.finddata import find_package_data

name = "turboblog"
version = "1.0.2rc2"
download_url = "http://cheeseshop.python.org/packages/2.4/"
download_url += "t/%(name)s/%(name)s-%(version)s-py2.4.egg" % {
    'name':name, 'version':version}

setup(
    name = name,
    version = version,
    description = "Blogging platform for TurboGears",
    author = "Eli Yukelzon, Florent Aide",
    author_email = "reflog@gmail.com, florent.aide@gmail.com",
    url = "http://turboblog.devjavu.com/",
    download_url = download_url,
    install_requires = ["TurboGears>=1.0.1", "SQLObject"],
    scripts = ["start-turboblog.py"],
    zip_safe = False,
    packages = find_packages(),
    package_data = find_package_data(
        where='turboblog',
        package='turboblog'),
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        "Framework :: TurboGears :: Applications"
        ],
    keywords = ["turbogears.app"],
    license = 'MIT',
    test_suite = 'nose.collector',
    )
    
