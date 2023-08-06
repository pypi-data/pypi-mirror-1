from setuptools import setup, find_packages

setup(
    name='kss.plugin.timer',
    version="0.1",
    #description="",
    author="Guido Wesdorp and Zest software",
    author_email="info@zestsoftware.nl",
    #url="",
    install_requires=["kss.base", "setuptools"],
    packages=find_packages(),
    namespace_packages=['kss', 'kss.plugin'],
    include_package_data=True,
    test_suite = 'kss.plugin.timer.tests.test_suite',
    entry_points={
        'kss.plugin': [
            'kss.plugin.timer=kss.plugin.timer.config:Kss.plugin.timer'
            ],
        },
)
