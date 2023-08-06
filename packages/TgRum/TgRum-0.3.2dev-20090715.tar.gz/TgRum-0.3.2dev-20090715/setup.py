from setuptools import setup

version = '0.3.2'

setup(name='TgRum',
    version=version,
    description="Some helpers to integrate Rum nicely into TurboGears",
    url='http://python-rum.org/',
    classifiers=[],
    keywords='Turbogears Rum wsgi',
    author='Alberto Valverde Gonzalez, Michael Brickenstein',
    author_email='info@python-rum.org',
    license='MIT',
    py_modules=["tgrum"],
    test_suite = "nose.collector",
    zip_safe=True,
    install_requires=[
        "Rum >= 0.3dev-20090708",
        "RumAlchemy >= 0.3dev-20090708",
        "tw.rum >= 0.3dev-20090708",
        "Turbogears2 >= 2.0b4",
        ]
    )
