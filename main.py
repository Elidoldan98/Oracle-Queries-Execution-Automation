import cx_Oracle
import pandas as pd
import re
import os

def connect_to_database():
    # Función para realizar la conexión a la base de datos
    dsn = cx_Oracle.makedsn('url', 'port', service_name='database name')
    connection = cx_Oracle.connect('user', 'password', dsn=dsn)
    return connection

def create_output_folder(output_folder):
    # Función para crear la carpeta de salida
    os.makedirs(output_folder, exist_ok=True)

def extract_queries(raw_text):
    # Función para extraer consultas SELECT, INSERT, DELETE y UPDATE
    lines = [line.strip() for line in raw_text.split('\n') if line.strip()]

    select_queries, insert_queries, delete_queries, update_queries = [], [], [], []
    query_accumulator = []

    for line in lines:
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

    return select_queries, insert_queries, delete_queries, update_queries

def execute_select_queries(connection, select_queries, output_folder, jira_number):
    # Función para ejecutar consultas SELECT y almacenar los resultados en un archivo Excel
    results_df = pd.DataFrame()

    if select_queries:
        try:
            with pd.ExcelWriter(os.path.join(output_folder, f'{jira_number}.xlsx'), engine='xlsxwriter') as excel_writer:
                with connection.cursor() as cursor:
                    for idx, select_query in enumerate(select_queries):
                        table_name_match = re.search(r'from\s+(\w+)', select_query, re.IGNORECASE)
                        table_name = table_name_match.group(1) if table_name_match else f'Sheet_{idx + 1}'

                        existing_sheets = excel_writer.sheets.keys()
                        original_table_name = table_name
                        suffix_number = 1

                        while table_name in existing_sheets:
                            table_name = f'{original_table_name}_Dup{suffix_number}'
                            suffix_number += 1

                        cursor.execute(select_query)
                        result_set = cursor.fetchall()

                        df = pd.DataFrame(result_set, columns=[desc[0] for desc in cursor.description])
                        df.to_excel(excel_writer, sheet_name=table_name, index=False)

                        if not results_df.empty:
                            results_df = pd.concat([results_df, df], ignore_index=True)
                        else:
                            results_df = df.copy()

            print("-" * 33)
            print(f"|{'BACKUP OK':^31}|")
            print("-" * 33)

        except cx_Oracle.DatabaseError as e:
            print(f"Error al ejecutar los comandos: {e}")
            connection.rollback()

    else:
        print("-" * 33)
        print(f"|{'NO BACKCUP':^20}|")
        print("-" * 33)

    return results_df

def execute_module_begin(connection, fsop):
    # Función para ejecutar el módulo begin
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"""
                begin
                    pre_ini_aplicacion;
                    pae_cnf.G_COD_MODULO:=1;
                end;
                --{fsop}
            """)
    except cx_Oracle.DatabaseError as e:
        print(f"Error el inciar modulo Begin: {e}")

def execute_queries(delete_queries, insert_queries, update_queries, connection):
    # Función para imprimir mensajes y ejecutar consultas DELETE, INSERT y UPDATE
    for delete_query in delete_queries:
        try:
            with connection.cursor() as cursor:
                cursor.execute(delete_query)
                rows_affected = cursor.rowcount

                print(delete_query)

                if rows_affected >= 200:
                    print(f"Rollback: rows affected => {rows_affected} for security verify query")
                    print('--------------------------------------')
                    connection.rollback()
                else:
                    print(f"Commit: rows affected => {rows_affected}")
                    print('-------------------------------')
                    connection.commit()

        except cx_Oracle.DatabaseError as e:
            print(f"Error: {e}")
            print('-------------')
            connection.rollback()

    for insert_query in insert_queries:
        try:
            with connection.cursor() as cursor:
                cursor.execute(insert_query)
                rows_affected = cursor.rowcount

            print(insert_query)
            connection.commit()
            print(f"Commit: Rows affected {rows_affected}")
            print('----------------------------')

        except cx_Oracle.DatabaseError as e:
            print(f"Error: {e}")
            print('-------------')
            connection.rollback()

    for update_query in update_queries:
        try:
            with connection.cursor() as cursor:
                cursor.execute(update_query)
                rows_affected = cursor.rowcount

                print(update_query)

                if rows_affected >= 150:
                    
                    print(f"Rollback: rows affected => {rows_affected} for security verify query")
                    print('---------------------------')
                    connection.rollback()
                else:
                    
                    print(f"Commit: rows affected => {rows_affected}")
                    print('---------------------------')
                    connection.commit()

        except cx_Oracle.DatabaseError as e:
            print(f"Error: \n {e}")
            print('-------------')
            connection.rollback()

def main():
    print(f'Current Database: Database NAME')

    connection = connect_to_database()
    create_output_folder(r'C:\IT\BK_FSOP')

    jira_number_digits = input("FSOP NUMBER ->  ")
    if not re.match(r'^\d{5}$', jira_number_digits):
        print("Error: Debe ingresar exactamente 5 dígitos.")
        exit()

    jira_number = f'{jira_number_digits}'

    raw_text = """



    """

    borde_cuadrado = "-" * 33

    select_queries, insert_queries, delete_queries, update_queries = extract_queries(raw_text)
    results_df = execute_select_queries(connection, select_queries, r'C:\IT\BK_FSOP', jira_number)
    execute_module_begin(connection, jira_number)

    
    print("Execute queries:")
    print(" ")

    execute_queries(delete_queries, insert_queries, update_queries, connection)

    connection.close()

if __name__ == "__main__":
    main()