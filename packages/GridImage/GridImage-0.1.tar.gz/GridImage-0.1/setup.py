from setuptools import setup, find_packages

setup(
    name = "GridImage",
    version = "0.1",
    packages = find_packages(),
    author = 'Carl Meyer',
    author_email = 'carl@dirtcircle.com',
    description = 'A simple command-line tool for generating an image for background tiling to confirm a CSS grid.',
    license = 'BSD',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    zip_safe = False,
    entry_points = {
            'console_scripts': [
                        'gridimage = gridimage:main',
                        ]}
)
