from setuptools import setup, find_packages
from turbogears.finddata import find_package_data

setup(
    name = "turboblog",
    version = "1.0.1",
    description = "Blogging platform for TurboGears",
    author = "Eli Yukelzon, Florent Aide",
    author_email = "reflog@gmail.com, florent.aide@gmail.com",
    url = "http://turboblog.dejavu.com/",
    download_url = "http://cheeseshop.python.org/packages/2.4/t/turboblog/turboblog-1.0.1-py2.4.egg",
    install_requires = ["TurboGears >= 1.0.1"],
    scripts = ["start-turboblog.py"],
    zip_safe = False,
    packages = find_packages(),
    package_data = find_package_data(
        where='turboblog',
        package='turboblog'),
    test_suite = 'nose.collector',
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
    )
    
