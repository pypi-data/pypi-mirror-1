try:
    from setuptools import setup, find_packages
except ImportError:
    raise SystemExit('Cannot import setuptools')

version = '0.1'

setup(
    name='simpledoc',
    version=version,
    description='Python document generator',
    license='MIT',
    install_requires=[
        'Pygments >= 1.0'
    ],
    url='http://alwaysmovefast.com',
    download_url='http://alwaysmovefast.com/download',
    author='David Reynolds',
    author_email='david@alwaysmovefast.com',
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    classifiers=[
        'Classifier: Development Status :: 4 - Beta',
        'Classifier: Topic :: Software Development :: Libraries :: Python Modules',
        'Classifier: Intended Audience :: Developers'
        'Classifier: Operating System :: OS Independent',
        'Classifier: Programming Language :: Python'
    ]
)
