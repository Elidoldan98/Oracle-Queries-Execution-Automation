print('Iniciando..')
import cx_Oracle
import pandas as pd
import re
import os

# Configuración de la conexión a la base de datos Oracle
dsn = cx_Oracle.makedsn('''url''', '''port''', service_name='''database name''')
connection = cx_Oracle.connect('user', 'password', dsn=dsn)

# Ruta donde se guardarán los archivos Excel
output_folder = r'C:\IT\BK'
os.makedirs(output_folder, exist_ok=True)

#esta parte del codigo se envia en las ejecuciones para consultas de auditoria
jira_url_base = "www.atlassian.net/browse/17831"

# Pedir número de referencia del link al usuario en este caso se usa JIRA
jira_number_digits = input("¿Cuál es el número del FSOP? ")
if not re.match(r'^\d{5}$', jira_number_digits):
    print("Error: Debe ingresar exactamente 5 dígitos.")
    exit()

# Completar el número del jira
jira_number = f'{jira_number_digits}'

# Texto en bruto con las consultas SELECT, INSERT, DELETE y UPDATE
raw_text = """
--Backup

select * from table_1 where code = '946274';

--A Aplicar

delete from ba_per_gen_ofertas a where a.cod_persona = 946274;
update ge_ing_clientes set estado = 'X' where person = 946274;

"""

# Dividir el texto en líneas y eliminar líneas vacías
lines = [line.strip() for line in raw_text.split('\n') if line.strip()]

# Inicializar listas de consultas SELECT, INSERT, DELETE y comandos UPDATE
select_queries = []
insert_queries = []
delete_queries = []
update_queries = []

# Analizar líneas y clasificar en SELECT, INSERT, DELETE o UPDATE
query_accumulator = []
for line in lines:
    # Eliminar comentarios al final de la línea
    line_without_comment = re.sub(r'--.*$', '', line).strip()

    if line_without_comment:
        query_accumulator.append(line_without_comment)

    if ';' in line:
        query_accumulator_str = ' '.join(query_accumulator)
        query_accumulator_str = query_accumulator_str.rstrip(';').strip()

        if re.match(r'^\s*select', query_accumulator_str, re.IGNORECASE):
            select_queries.append(query_accumulator_str)
        elif re.match(r'^\s*insert', query_accumulator_str, re.IGNORECASE):
            insert_queries.append(query_accumulator_str)
        elif re.match(r'^\s*delete', query_accumulator_str, re.IGNORECASE):
            delete_queries.append(query_accumulator_str)
        elif re.match(r'^\s*update', query_accumulator_str, re.IGNORECASE):
            update_queries.append(query_accumulator_str)

        query_accumulator = []

# Crear un DataFrame para almacenar los resultados de las consultas SELECT
results_df = pd.DataFrame()

# Crear un DataFrame para almacenar los resultados de las consultas SELECT
results_df = pd.DataFrame()

# Ejecutar consultas SELECT y almacenar en el DataFrame
try:
    # Crear el escritor de Excel
    with pd.ExcelWriter(os.path.join(output_folder, f'{jira_number}.xlsx'), engine='xlsxwriter') as excel_writer:

        with connection.cursor() as cursor:
            for idx, select_query in enumerate(select_queries):
                # Obtener el nombre de la tabla desde la consulta SELECT
                table_name_match = re.search(r'from\s+(\w+)', select_query, re.IGNORECASE)
                table_name = table_name_match.group(1) if table_name_match else f'Sheet_{idx + 1}'

                # Verificar si ya existe una hoja con el mismo nombre
                existing_sheets = excel_writer.sheets.keys()
                original_table_name = table_name
                suffix_number = 1

                while table_name in existing_sheets:
                    table_name = f'{original_table_name}_Dup{suffix_number}'
                    suffix_number += 1

                cursor.execute(select_query)
                result_set = cursor.fetchall()

                # Crear un DataFrame para cada conjunto de resultados
                df = pd.DataFrame(result_set, columns=[desc[0] for desc in cursor.description])

                # Agregar el DataFrame a la hoja correspondiente
                df.to_excel(excel_writer, sheet_name=table_name, index=False)

                # Verificar si el DataFrame principal ya tiene datos antes de concatenar
                if not results_df.empty:
                    # Concatenar los resultados al DataFrame principal
                    results_df = pd.concat([results_df, df], ignore_index=True)
                else:
                    # Si el DataFrame principal está vacío, simplemente asignar el DataFrame actual
                    results_df = df.copy()

    print(f"Backup Realizado correctamente en {output_folder}")
    fsop = jira_url_base + jira_number
    print(fsop)

    # Ejecutar módulo begin, este modulo solo es necesario en sistemas ITGF porque no se pueden hacer modificaciones en la base sin ese sistema. 
    # el "--{fsop}" hace referencia al link de la ejecucion solo es necesario si se tiene auditoria
    try:
        with connection.cursor() as cursor:
            # Ejecutar módulo begin
            cursor.execute(f"""
                begin
                    pre_ini_aplicacion;
                    pae_cnf.G_COD_MODULO:=1;
                end;
                
                --{fsop}
                
            """)
        print("Begin execute successfully")
    except cx_Oracle.DatabaseError as e:
        print(f"Error al ejecutar el módulo begin: {e}")
    #imprimir carga de link fsop
    print(f'Enlace fsop cargado = > {fsop}')
    
    

    # Ejecutar comandos DELETE 
    for delete_query in delete_queries:
        try:
            with connection.cursor() as cursor:
                cursor.execute(delete_query)
                rows_affected = cursor.rowcount  # Obtener el número de filas afectadas

                print(f"{delete_query}\nRows affected: {rows_affected}\n")

                #por seguridad o en caso de que el query no tenga "where" se toleran hasta 200 lineas afectadas, si supera ese numero se hace un rollback, 
                
                if rows_affected >= 200:
                    print(f"Rollback: rows affected => {rows_affected}")
                    connection.rollback()
                #commit en caso de ejecucion correcta
                else:
                    print(f"Commit: rows affected => {rows_affected}")
                    connection.commit()

            
        except cx_Oracle.DatabaseError as e:
            print(f"Error DELETE: {e}")
            connection.rollback()  # Rollback en caso de error

    # Ejecutar comandos INSERT
    # Los insert no tienen la seguridad de 200 lineas, se puede implementar de ser necesario
    for insert_query in insert_queries:
        try:
            with connection.cursor() as cursor:
                cursor.execute(insert_query)
                rows_affected = cursor.rowcount #Obtener el numero de fials afectadas
                
            print(f"{insert_query}")
            
            connection.commit()
                
            print(f"Commit: Rows affected {rows_affected}")
        except cx_Oracle.DatabaseError as e:
            print(f"Error INSERT: {e}")
            connection.rollback()  # Rollback en caso de error

    # Ejecutar comandos UPDATE 
    for update_query in update_queries:
        try:
            with connection.cursor() as cursor:
                cursor.execute(update_query)
                rows_affected = cursor.rowcount  # Obtener el número de filas afectadas

                print(f"{update_query}\nRows affected: {rows_affected}\n")

                if rows_affected >= 150:
                    print(f"Rollback: rows affected => {rows_affected}")
                    connection.rollback()
                else:
                    print(f"Commit: rows affected => {rows_affected}")
                    connection.commit()

            
        except cx_Oracle.DatabaseError as e:
            print(f"Error UPDATE: \n {e}")
            connection.rollback()  # Rollback en caso de error

except cx_Oracle.DatabaseError as e:
    print(f"Error al ejecutar los comandos: {e}")
    connection.rollback()  # Rollback en caso de error

# Cerrar conexión
connection.close()
