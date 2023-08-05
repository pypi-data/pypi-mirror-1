from setuptools import setup

setup(
    name='pyorbited',
    version='0.2.0',
    author='Michael Carter',
    author_email='CarterMichael@gmail.com',
    license='MIT License',
    url="http://www.orbited.org",
    download_url="http://www.orbited.org/download.html",
    description='A python client for Orbited (Orbit Event Daemon), a COMET server. Includes three implementations: pyevent, twisted, basic sockets.',
    packages=[
        'pyorbited',
    ],
    install_requires=[
        "demjson >= 1.1"
    ],
    zip_safe = False,
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)
