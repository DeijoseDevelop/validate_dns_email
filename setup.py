import pathlib
from setuptools import find_packages, setup

HERE = pathlib.Path(__file__).parent

VERSION = '0.1.0'  # Muy importante, deberéis ir cambiando la versión de vuestra librería según incluyáis nuevas funcionalidades
# Debe coincidir con el nombre de la carpeta
PACKAGE_NAME = 'validate_dns_email'
AUTHOR = 'Deiver Jose Vazquez Moreno'  # Modificar con vuestros datos
AUTHOR_EMAIL = 'estudiandovazmore@gmail.com'  # Modificar con vuestros datos
# Modificar con vuestros datos
URL = 'https://github.com/DeijoseDevelop/validate_dns_email'

LICENSE = 'MIT'  # Tipo de licencia
DESCRIPTION = 'Library to validate emails with dns.'  # Descripción corta
# Referencia al documento README con una descripción más elaborada
LONG_DESCRIPTION = (HERE / "README.md").read_text(encoding='utf-8')
LONG_DESC_TYPE = "text/markdown"


# Paquetes necesarios para que funcione la librería. Se instalarán a la vez si no lo tuvieras ya instalado
INSTALL_REQUIRES = [
    'py3dns==3.2.1'
]

setup(
    name=PACKAGE_NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type=LONG_DESC_TYPE,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    install_requires=INSTALL_REQUIRES,
    license=LICENSE,
    packages=find_packages(),
    include_package_data=True
)
