Descripción
===========

Este paquete provee tipos de contenido para normativas. Los tipos de contenido
provistos son:
 * Area: Un tipo especial de carpeta donde se guardarán normativas. Contendrá
información sobre los emisores que puedan crear normativas en ella. Las áreas
se crean desde el menú desplegable para agregar contenido en la raíz del
portal.
 * Normativa: Un tipo de contenido que representa una normativa, con metadatos,
relaciones con otras normativas, un documento PDF principal, y adjuntos. Las
normativas se crean con el link de Agregar Normativa en la vista de cada área.
 * Attachment: Adjuntos que pueden agregarse a una Normativa. Se los administra
desde la pestaña "Administrar Adjuntos" en la vista de cada Normativa.

Crea una utilidad para administrar tipos de normativas en el panel de control.

Permite incorporar al sitio un portlet de búsqueda de normativas desde el
administrador de portlets de Plone.

Permite enviar normativas a los usuarios seleccionados de la libreta de
direcciones asociada al área. La libreta de direcciones se edita desde la
edición de un área. Las normativas se envían desde el enlace Enviar Normativa
en la vista de un área.


Dependencias
============

Este producto debería funcionar en toda la serie de Plone 3. Sin embargo sólo
fue probado con Plone 3.3rc2. Los siguientes productos tienen que estar
instalados en el sitio antes de instalar Products.DigestoContentTypes:

  * Products.CMFPlacefulWorkflow (el cuál viene con Plone)
  * Products.ATExtensions 0.9.5
  * iw.fss 2.7.6
  * Products.ATBackRef 2.0


Instalación
===========

Instalar las dependencias y luego instalar el producto DigestoContentTypes
desde el panel de control, Productos Adicionales. Si estás usando zc.buildout
sólo hay que agregar Products.DigestoContentTypes a los eggs y zcml y
reconstruir el buildout.

Un buildout de ejemplo se puede encontrar en el repositorio SVN del producto:
http://svn.plone.org/svn/collective/Products.DigestoContentTypes/buildout. Este
buildout puede usarse para probar el producto de una forma rápida o como base
para modificar tu propio buildout.


Búsqueda de normativas
======================

Para poder encontrar normativas según diferentes criterios de búsqueda en la
búsqueda avanzada, se agregan como índices del catálogo los siguientes campos
de las normativas: Fecha, Emisor, Número, Deroga a, Modifica a, Es derogada
por, Tipo ,Abreviatura, Area, CUDAP.

Para los requerimientos de la búsqueda "live", se indexan como SearchableText
los siguientes: Título, Descripción, nombre y contenido del archivo PDF,
Número, Número de expediente, CUDAP.


Desarrollo
==========

Este producto fue desarrollado usando ArgoUML y ArchgenXML 2.4.1. Los tipos de
contenido fueron modelados como clases en un diagrama de clases UML y luego se
utilizó la herramienta ArchGenXML que genera un producto Plone a partir de un
modelo de clases UML. Dicho producto provee tipos de contenidos para las clases
del diagrama. El diagrama está disponible dentro del código del producto:
model/DigestoContentTypes.zargo.

Cada vez que se realiza una modificación a este producto debe preservarse la
sincronía entre el modelo UML y el código generado. Esto se logra siguiendo
esta guía (de items algo redundantes):
* Si hay que introducir cambios al producto, primero se busca la forma de
hacerlo modificando el modelo UML y regenerando el producto. Sólo si esto no es
posible o si resulta impráctico, se buscan otras formas de introducir las
modificaciones.
* Si se modifica el modelo, regenerar el producto usando ArchGenXML.
* Si se agrega código, hacerlo en las áreas que provee ArchGenXML de forma que
si se regenera el producto no se remuevan el código agregado.

Para regenerar el producto ejecutar en el directorio model el siguiente
comando: archgenxml --cfg=agx.cfg -o ../ DigestoContentTypes.zargo

El producto cuenta con pruebas funcionales y de unidad automatizadas. Estas se
pueden encontrar en el directorio "tests". Cuando se introducen modificaciones
al producto se deben agregar pruebas de antemano y las modificaciones deben
permitir que las pruebas existentes sigan pasando. En un entorno buildout, la
forma de ejecutar las pruebas para este producto sería:
bin/instance test -s Products.DigestoContentTypes.

El producto cuenta con dos perfiles de extensión GenericSetup: default y extra;
ambos en el directorio "profiles". El perfil "default" es en su mayor parte
generado por ArchGenXML y desafortunadamente no provee puntos de
personalización en ciertos archivos, por lo tanto se creó el perfil "extra"
donde se agregan aquellos pasos que no se podrían agregar al perfil "default"
porque serían pisados al regenerar el producto a partir del modelo UML.

El buildout de desarrollo se puede construir ejecutando los siguientes
comandos:

$ svn co http://svn.plone.org/svn/collective/Products.DigestoContentTypes/buildout digesto
$ cd digesto
$ python2.4 bootstrap.py
$ ./bin/buildout

La instancia se inicia con:

$ ./bin/instance fg

La ZMI se accede desde http://localhost:8080/manage, donde nos podemos
autenticar usando 'admin' como usuario y contraseña.

Referencias acerca de prácticas y herramientas utilizadas en el desarrollo de
este producto:

* ArchGenXML 2 - Developers Manual:
  http://plone.org/documentation/manual/archgenxml2
* Testing in Plone 
  http://plone.org/documentation/tutorial/testing/


Créditos
========

Este producto fue desarrollado por Emanuel Sartor y Santiago Bruno de Menttes.
El desarrollo fue patrocinado por la Universidad Nacional de Córdoba y Menttes.


Reconocimientos
===============

Por favor revisar la sección "Acknowlegements" del archivo README.txt.
