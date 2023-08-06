from distutils.core import setup
import sys

py_version_t = sys.version_info[:2]
py_version_s = ".".join([str(x) for x in py_version_t])

if __name__ == '__main__':
    version_ext = ""
    if 'sdist' in sys.argv:
        version_ext = '-py'+py_version_s

    setup(
        name = 'generator_tools',
        version = '0.3.2'+version_ext,
        description = 'generator_tools enable copying and pickling generators',
        author = 'Kay Schluehr',
        author_email = 'kay@fiber-space.de',
        url = 'http://www.fiber-space.de/',
        download_url = 'http://www.fiber-space.de/downloads/download.html',
        license = "BSD",
        packages = ['generator_tools',
                    'generator_tools.tests',
                    ],
        package_data={'': ['LICENSE.txt'],
                      'generator_tools': ['doc/*.html',
                                          'doc/*.png']},
    )

