# Automatización de Backup y Ejecuciones en de Bases de Datos Oracle

Este repositorio contiene un script en Python que automatiza la creación de backups y la ejecución de comandos en una base de datos Oracle. El script utiliza cx_Oracle y pandas para interactuar con la base de datos y generar archivos Excel con los resultados de las consultas SELECT.

## Estructura de Carpetas

- `main.py`: Contiene el script principal.
- `Ejemplos/`: Ejemplos de consultas y como guarda los backups en los archivos excell. 
- `Resultados/`: Carpeta donde se almacenan los archivos Excel generados, esta ruta se puede cambiar a gusto

## Requisitos de Software

- Python 3.x
- Bibliotecas: cx_Oracle, pandas, XlsxWriter

## Instrucciones de Configuración

1. Instalar las dependencias utilizando `pip install -r requirements.txt`.
2. Configurar la conexión a la base de datos en el script.

## Instrucciones de Ejecución

1. Pegar las ejecuciones en la variable 'raw_text' en archivo main.py las ejecuciones
   tienen que tener este formato especifico para que el script lo pueda selecionar de manera correcta.
      Ejemplo:
        Select * from table_1 where cod_user = '12345';
   El script selecciona todo lo que este entre un "select", "update", "insert" o "delete" hasta un ";"
    
3. Ejecutar el script principal (`main.py`).
2. Ingresar el número del link de referencia cuando se solicite (actualmente el script acepta 5 digitos si no da un error, esto se puede cambiar a gusto) 
3. Verificar los archivos Excel generados en la carpeta `Resultados/`.
4. Verificar si las sentencias Update, Delete, Insert corrieron correctamente. 

## Contacto

Para preguntas o comentarios, contáctame en eliasdoldan7@gmail.com


## Licencia

Este proyecto está bajo la licencia MIT 
MIT License (Modified)

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

**Commercial use is not allowed without prior written permission from the copyright holder.**

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
