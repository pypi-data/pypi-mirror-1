from paver import setuputils

setup_meta=dict(
    name='Paver',
    version="0.4",
    description='Easy build, distribution and deployment scripting',
    long_description="""Paver is a Python-based build/distribution/deployment scripting tool along the
lines of Make or Rake. What makes Paver unique is its integration with 
commonly used Python libraries. Common tasks that were easy before remain 
easy. More importantly, dealing with *your* applications specific needs and 
requirements is also easy.""",
    author='Kevin Dangoor',
    author_email='dangoor+paver@gmail.com',
    url='http://www.blueskyonmars.com/projects/paver/',
    packages=['paver'],
    package_data=setuputils.find_package_data("paver", package="paver",
                                            only_in_packages=False),
    install_requires=[],
    test_suite='nose.collector',
    zip_safe=False,
    entry_points="""
    [console_scripts]
    paver = paver.command:main
    """,
)
