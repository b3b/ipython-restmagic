from setuptools import setup, convert_path

main_ns = {}
ver_path = convert_path('restmagic/version.py')
with open(ver_path) as ver_file:
    exec(ver_file.read(), main_ns)


setup(
    name='ipython-restmagic',
    version=main_ns['__version__'],
    packages=['restmagic'],
    description='HTTP REST magic for IPython',
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
        'Development Status :: 1 - Planning',
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Framework :: IPython',
        'Topic :: Internet :: WWW/HTTP',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 2',
    ],
    keywords='magic rest http ipython jupyter',
    license='MIT',
    zip_safe=False,
)
