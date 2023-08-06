try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name='Refaction',
    version='0.0.1',
    summary='Redistribute Webfaction',
    description='''Web-based interface for sharing webfaction services using webfaction's API.''',
    author='Emanuel Calso',
    author_email='egcalso@gmail.com',
    #url='',
    install_requires=["Pylons>=0.9.6.1", "PyCRUD"],
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    test_suite='nose.collector',
    package_data={'refaction': ['i18n/*/LC_MESSAGES/*.mo']},
    #message_extractors = {'refaction': [
    #        ('**.py', 'python', None),
    #        ('templates/**.mako', 'mako', None),
    #        ('public/**', 'ignore', None)]},
    entry_points="""
    [paste.app_factory]
    main = refaction.config.middleware:make_app

    [paste.app_install]
    main = pylons.util:PylonsInstaller
    """,
)
