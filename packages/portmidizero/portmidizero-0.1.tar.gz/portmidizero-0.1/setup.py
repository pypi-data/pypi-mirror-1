from distutils.core import setup

setup(
    name='portmidizero',
    version='0.1',
    description='Python ctypes bindings for PortMidi',
    author='Grant Yoshida',
    author_email='enoki.enoki@gmail.com',
    packages=['portmidizero'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: MacOS :: MacOS X',
        'Programming Language :: Python',
        'Topic :: Multimedia :: Sound/Audio :: MIDI',
        'Topic :: Software Development',
    ],
    license='MIT License',
    url = 'http://gitorious.org/projects/portmidizero',
    description='A wrapper for PortMidi using ctypes.',
    long_description = '''
    portmidizero is a simple wrapper for PortMidi in pure python.

    It's intended as an easier to install version of pyPortMidi:
    it doesn't require a compiler or any external python packages.

    Its only dependency, besides a dynamically linked PortMidi library,
    is ctypes.
    '''
)
