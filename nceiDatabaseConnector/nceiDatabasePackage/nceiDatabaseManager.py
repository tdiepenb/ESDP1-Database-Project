import psycopg2
from psycopg2 import sql
from concurrent.futures import ThreadPoolExecutor
import os
import numpy as np


class NCEIDatabaseManager:
    def __init__(self, db_name="mydatabase", db_user="myuser", db_password="mypassword", db_host="localhost",
                 db_port="5432"):
        self.db_name = db_name
        self.db_user = db_user
        self.db_password = db_password
        self.db_host = db_host
        self.db_port = db_port
        self.connection = None
        self.cursor = None
        self.connect_to_db()

    def connect_to_db(self):
        try:
            self.connection = psycopg2.connect(
                dbname=self.db_name,
                user=self.db_user,
                password=self.db_password,
                host=self.db_host,
                port=self.db_port
            )
            self.cursor = self.connection.cursor()
            print(f"Connected to database {self.db_name} with user {self.db_user}")
        except Exception as error:
            print(f"Error: {error}")

    def close_connection(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        print("Database connection closed.")

    def insert_copy(self, file_path="", table_name="", columns=None):
        if columns is None:
            columns = []
        try:
            copy_command = sql.SQL("""
                COPY {table} ({columns}) FROM STDIN WITH CSV HEADER
            """).format(
                table=sql.Identifier(table_name),
                columns=sql.SQL(',').join(map(sql.Identifier, columns))
            )
            print(f"Copying file {file_path} to database {table_name}")
            with open(file_path, 'r') as file:
                self.cursor.copy_expert(copy_command, file)
            self.connection.commit()
            print(f"Insert with copy of file {file_path} to table: {table_name} done.")
            self.cursor.execute(f'SELECT COUNT(*) FROM "{table_name}"')
            row_count = self.cursor.fetchone()[0]
            print(f"Row count after insertion in table {table_name}: {row_count}")
        except Exception as error:
            print(f"Error: {error}")
            if self.connection:
                self.connection.rollback()

    def create_stations_table(self):
        name = "Station"
        try:
            table_name = sql.Identifier(name)
            columns = [
                sql.Identifier("id"), sql.Identifier("latitude"), sql.Identifier("longitude"),
                sql.Identifier("elevation"), sql.Identifier("state"), sql.Identifier("name"),
                sql.Identifier("gsn_flag"), sql.Identifier("hcn_crn_flag"), sql.Identifier("wmo_id")
            ]
            column_types = [
                sql.SQL("VARCHAR(100) PRIMARY KEY"), sql.SQL("FLOAT"), sql.SQL("FLOAT"),
                sql.SQL("FLOAT"), sql.SQL("VARCHAR(100)"), sql.SQL("VARCHAR(100)"),
                sql.SQL("VARCHAR(100)"), sql.SQL("VARCHAR(100)"), sql.SQL("VARCHAR(100)")
            ]
            create_table_command = sql.SQL('''
                CREATE TABLE IF NOT EXISTS {table} (
                    {id} {id_type},
                    {latitude} {latitude_type},
                    {longitude} {longitude_type},
                    {elevation} {elevation_type},
                    {state} {state_type},
                    {name} {name_type},
                    {gsn_flag} {gsn_flag_type},
                    {hcn_crn_flag} {hcn_crn_flag_type},
                    {wmo_id} {wmo_id_type}
                )
            ''').format(
                table=table_name,
                id=columns[0], id_type=column_types[0],
                latitude=columns[1], latitude_type=column_types[1],
                longitude=columns[2], longitude_type=column_types[2],
                elevation=columns[3], elevation_type=column_types[3],
                state=columns[4], state_type=column_types[4],
                name=columns[5], name_type=column_types[5],
                gsn_flag=columns[6], gsn_flag_type=column_types[6],
                hcn_crn_flag=columns[7], hcn_crn_flag_type=column_types[7],
                wmo_id=columns[8], wmo_id_type=column_types[8]
            )
            self.cursor.execute(create_table_command)
            self.connection.commit()
            print(f"{name} table created.")
        except Exception as error:
            print(f"Error: {error}")
            if self.connection:
                self.connection.rollback()

    def create_climate_table(self, year):
        table_name = f"Climate{year}"
        station_table = "Station"
        try:
            create_table_command = sql.SQL('''
                CREATE TABLE IF NOT EXISTS {table} (
                    id SERIAL PRIMARY KEY,
                    stationcode VARCHAR(50) REFERENCES {station_table}(id),
                    datelabel DATE,
                    param VARCHAR(10),
                    value FLOAT,
                    mflag VARCHAR(10),
                    qflag VARCHAR(10),
                    sflag VARCHAR(10),
                    time CHAR(4)
                )
            ''').format(
                table=sql.Identifier(table_name),
                station_table=sql.Identifier(station_table),
            )
            self.cursor.execute(create_table_command)
            self.connection.commit()
            print(f"Table {table_name} created successfully.")
        except Exception as error:
            print(f"Error: {error}")
            if self.connection:
                self.connection.rollback()
        return table_name

    def drop_table(self, table_name):
        try:
            drop_table_command = sql.SQL("DROP TABLE IF EXISTS {table}").format(table=sql.Identifier(table_name))
            self.cursor.execute(drop_table_command)
            self.connection.commit()
            print(f"Table {table_name} dropped successfully.")
        except Exception as error:
            print(f"Error: {error}")
            if self.connection:
                self.connection.rollback()

    def count_rows(self, table_name):
        try:
            count_command = sql.SQL('SELECT COUNT(*) FROM {table}').format(
                table=sql.Identifier(table_name)
            )
            self.cursor.execute(count_command)
            row_count = self.cursor.fetchone()[0]
            print(f"The table {table_name} contains {row_count} rows.")
        except Exception as error:
            print(f"Error: {error}")
            if self.connection:
                self.connection.rollback()

    def split_csv_file(self, file_path, num_chunks):

        with open(file_path, 'r') as file:
            header = file.readline()
            lines = file.readlines()

        print(f"Total Number of lines: {len(lines)}")
        lines_per_chunk = int(np.ceil(len(lines) / num_chunks))
        print(f"Chunk size is {lines_per_chunk}")

        print(f"Splitting {file_path} into {num_chunks} chunks of size {lines_per_chunk}.")

        file_base, file_ext = os.path.splitext(file_path)

        with open(file_path, 'r') as f:
            header = f.readline()
            chunk_number = 0
            chunk_lines = []
            for i, line in enumerate(f):
                chunk_lines.append(line)
                if (i + 1) % lines_per_chunk == 0:
                    print(
                        f"Writing chunk {chunk_number} file to {file_base}_chunk{chunk_number}{file_ext} with size {len(chunk_lines)}")
                    chunk_file_path = f"{file_base}_chunk{chunk_number}{file_ext}"
                    with open(chunk_file_path, 'w') as chunk_file:
                        chunk_file.write(header)
                        chunk_file.writelines(chunk_lines)
                    chunk_lines = []
                    chunk_number += 1
            # Write remaining lines to the last chunk
            if chunk_lines:
                chunk_file_path = f"{file_base}_chunk{chunk_number}{file_ext}"
                with open(chunk_file_path, 'w') as chunk_file:
                    chunk_file.write(header)
                    chunk_file.writelines(chunk_lines)
        return [f"{file_base}_chunk{chunk_number}{file_ext}" for chunk_number in range(chunk_number + 1)]

    def multi_threaded_insert(self, file_path, table_name, columns=None, num_threads=4):
        if columns is None:
            columns = []

        # this splits the file into equal sized chunks. That way one thread shouldn't finish that much earlier than an other and we use resources efficently
        chunks = self.split_csv_file(file_path, num_threads)

        def insert_chunk(chunk_file):
            # we can't use the standard connection here since each thread needs its own connection
            print(f'Thread started for chunk: {chunk_file}')
            try:
                conn = psycopg2.connect(
                    dbname=self.db_name,
                    user=self.db_user,
                    password=self.db_password,
                    host=self.db_host,
                    port=self.db_port
                )
                cur = conn.cursor()
                copy_command = sql.SQL("""
                    COPY {table} ({columns}) FROM STDIN WITH CSV HEADER
                """).format(
                    table=sql.Identifier(table_name),
                    columns=sql.SQL(',').join(map(sql.Identifier, columns))
                )

                with open(chunk_file, 'r') as chunk:
                    # this adds the chunk to the database using copy statement
                    cur.copy_expert(copy_command, chunk)
                conn.commit()
                print(f'Thread for chunk {chunk_file} completed.')
            except Exception as error:
                print(f"Error in thread: {error}")
                if conn:
                    conn.rollback()
            finally:
                cur.close()
                conn.close()
                os.remove(chunk_file)

        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(insert_chunk, chunk_file) for chunk_file in chunks]
            for future in futures:
                try:
                    future.result()
                except Exception as e:
                    print(f"An error occurred: {e}")

        self.count_rows(table_name)
        print(f"Multi-threaded insert completed for {table_name}.")
