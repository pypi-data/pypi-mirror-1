try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name='darcs-cgi',
    version='0.01.001',
    description='provides authenticated access to darcs repositories',
    author='orbisvicis',
    author_email='orbisvicis@gmail.com',
    url='',
    install_requires=[
        "Pylons>=0.9.7",
        "lxml>=2.2",
        "pygpgme>=0.8.1"
    ],
    setup_requires=["PasteScript>=1.6.3"],
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    test_suite='nose.collector',
    package_data={'darcscgi': ['i18n/*/LC_MESSAGES/*.mo']},
    #message_extractors={'darcscgi': [
    #        ('**.py', 'python', None),
    #        ('templates/**.mako', 'mako', {'input_encoding': 'utf-8'}),
    #        ('public/**', 'ignore', None)]},
    zip_safe=False,
    paster_plugins=['PasteScript', 'Pylons'],
    entry_points="""
    [paste.app_factory]
    main = darcscgi.config.middleware:make_app

    [paste.app_install]
    main = pylons.util:PylonsInstaller
    """,
)
