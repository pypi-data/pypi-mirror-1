from setuptools import setup, find_packages

setup(
    name="RecentPosts",
    version="0.1",
    description="Recent posts plugin for TB sidebar",
    author="reflog",
    author_email="reflog@gmail.com",
    url="http://www.turboblog.org/plugins/",
    download_url="http://www.turboblog.org/plugins",
    license="MIT",
#    install_requires = ["kid >= 0.8.0"],
    zip_safe=False,
    packages=find_packages(),
    classifiers = [
        'Development Status :: 3 - Alpha',
        #'Environment :: TurboGears',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    entry_points="""
    [turboblog.plugins.sidebar]
    recent = recentposts.plugin:RecentPostsPlugin
    """,
    test_suite = 'nose.collector',
    )
    
