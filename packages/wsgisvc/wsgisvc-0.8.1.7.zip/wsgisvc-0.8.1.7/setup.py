try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name='wsgisvc',
    version="0.8.1.7",
    description='A script to install paste deployment configurations as windows services.',
    author='Tibor Arpas',
    author_email='tibor.arpas@infinit.sk',
    install_requires=['PasteScript','PrettyTable'], #  And Mark Hammonds pywin32 
    include_package_data=True,
    py_modules=['wsgisvc','TestApp','TestWsgisvc'],
    classifiers=["Development Status :: 4 - Beta"],
    license = "Apache 2.0",
    entry_points = """
    [console_scripts]
    wsgisvc = wsgisvc:main
    
    [paste.app_factory]
        main = TestApp:paste_deploy_app
 """,
)
