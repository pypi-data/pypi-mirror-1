from setuptools import setup, find_packages

setup(
    name="TurboCheetah",
    version="0.9.5",
    description="""TurboGears plugin to support use of Cheetah templates.""",
    long_description="""This template plugin can be used with TurboGears
or Buffet. The development version is here:
http://www.turbogears.org/svn/turbogears/trunk/plugins/cheetah/#egg=TurboCheetah-dev""",
    author="Kevin Dangoor",
    author_email="dangoor+turbogears@gmail.com",
    url="http://www.turbogears.org/docs/plugins/template.html",
    download_url="http://www.turbogears.org/download/",
    keywords=["python.templating.engines", "turbogears"],
    license="MIT",
    install_requires = ["Cheetah >= 1.0"],
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
    [python.templating.engines]
    cheetah = turbocheetah.cheetahsupport:TurboCheetah
    """,
    test_suite = 'nose.collector',
    )
    
