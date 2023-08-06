try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name='frla',
    version="0.0.1",
    description='FreeRadius Log Analyser for PostGreSQL',
    author='Mehtap Tamturk',
    author_email='mehtaptamturk@gmail.com',
    #url='http://127.0.0.1:5000/index.html',
    install_requires=["Pylons>=0.9.6.2"],
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    test_suite='nose.collector',
    package_data={'frla': ['i18n/*/LC_MESSAGES/*.mo']},
    message_extractors = {'frla': [
            ('**.py', 'python', None),
            ('templates/**.mako', 'mako', None),
            ('public/**', 'ignore', None)]},
    entry_points="""
    [paste.app_factory]
    main = frla.config.middleware:make_app

    [paste.app_install]
    main = pylons.util:PylonsInstaller
    """,
)
