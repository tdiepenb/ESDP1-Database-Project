import psycopg2

def create_connection(dbname="mydatabase", user="myuser", password="mypassword", host="localhost", port="5432"):
    try:
        connection = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,  # Connect to the host where Docker is running
            port=port
        )
        cursor = connection.cursor()

        return connection, cursor
    
    except Exception as error:
        print(f"Error: {error}")
    
    finally:
        if connection:
            cursor.close()
            connection.close()

str = f'''
                    CREATE TABLE IF NOT EXISTS {False} (
                        id SERIAL PRIMARY KEY,
                        stationcode VARCHAR(50),
                        datelabel DATE,
                        param VARCHAR(10),
                        value FLOAT,
                        mflag VARCHAR(10),
                        qflag VARCHAR(10),
                        sflag VARCHAR(10)
                    )
                '''

def create_table(tablename = "", columnspecs = ""):
    try:
        connection = create_connection()[0]
        cursor = create_connection()[1]

        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {tablename} ({columnspecs})
        ''')
        print("Done")

        # Commit changes
        connection.commit()

    except Exception as error:
        print(f"Error: {error}")
    
    finally:
        if connection:
            cursor.close()
            connection.close()


#stationcode, datelabel, param, value, mflag, qflag, sflag,time
def insert_copy(file_path = "", table_name="", columns= []):
    try:
        connection = create_connection()[0]
        cursor = create_connection()[1]
        
        with open(file_path, 'r') as file:
            cursor.copy_expert(f"COPY {table_name} ({",".join(columns)}) FROM STDIN WITH CSV HEADER", file)

        print(f"Insert with copy of file {file_path} to table: {table_name} done.")

        # Commit changes
        connection.commit()

    except Exception as error:
        print(f"Error: {error}")
    
    finally:
        if connection:
            cursor.close()
            connection.close()
