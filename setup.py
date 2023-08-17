import os
import re
import setuptools

path = os.path.dirname(os.path.abspath(__file__))
with open('{}/requirements.txt'.format(path), 'r', encoding='utf-8') as file:
    # Match an valid requirement without matching a comment
    install_requires = re.findall(r'^[^#].*$', file.read(), re.MULTILINE)

setuptools.setup(
    name='sleepy',
    author='Evan McBroom',
    description='Lexer and parser for the Sleep scripting language.',
    packages=setuptools.find_packages(where=path),
    python_requires='>=3.7',
    install_requires=install_requires,
    extras_require={
        'dev': ['check-manifest']
    }
)