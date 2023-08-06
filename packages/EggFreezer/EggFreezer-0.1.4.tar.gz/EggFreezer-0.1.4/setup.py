from setuptools import setup

version = '0.1.4'

def get_description():
    lines = []
    for line in open('eggfreezer.py').readlines()[1:]:
        if line.startswith('"""'): break
        lines.append(line)
    return ''.join(lines)


setup(name='EggFreezer',
    version=version,
    description="Creates single-file installers for eggified distributions",
    download_url='http://toscawidgets.org/download',
    long_description=get_description(),
    classifiers=[],
    author='Alberto Valverde Gonzalez',
    author_email='alberto@toscat.net',
    license='MIT',
    py_modules=["eggfreezer"],
    zip_safe=True,
    install_requires=["virtualenv >= 1.1"],
    entry_points="""
    [console_scripts]
    eggfreezer = eggfreezer:main
    """,
    )
