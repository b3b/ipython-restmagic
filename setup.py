from setuptools import setup, convert_path

main_ns = {}
with open(convert_path('restmagic/version.py')) as ver_file:
    exec(ver_file.read(), main_ns)

with open(convert_path('README.rst')) as readme_file:
    long_description = readme_file.read()


setup(
    name='restmagic',
    version=main_ns['__version__'],
    packages=['restmagic'],
    description='HTTP REST magic for IPython',
    long_description=long_description,
    long_description_content_type='text/x-rst',
    author='b3b',
    author_email='ash.b3b@gmail.com',
    install_requires=[
        'ipython>=1.0',
        'requests-toolbelt>=0.8.0',
        'six',
    ],
    url='https://github.com/b3b/ipython-restmagic',
    # https://pypi.org/classifiers/
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Framework :: IPython',
        'Framework :: Jupyter',
        'Topic :: Internet :: WWW/HTTP',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='magic rest http ipython jupyter',
    license='MIT',
    zip_safe=False,
)
