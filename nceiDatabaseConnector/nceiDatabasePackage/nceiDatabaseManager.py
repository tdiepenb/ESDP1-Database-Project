import psycopg2
from psycopg2 import sql
from concurrent.futures import ThreadPoolExecutor
import os
import numpy as np
import pandas as pd


class NCEIDatabaseManager:
    def __init__(self, db_name="mydatabase", db_user="myuser", db_password="mypassword", db_host="localhost",
                 db_port="5432",
                 weather_cols=None, station_cols=None, debug_messages = False):

        if weather_cols is None:
            weather_cols = ["id", "stationcode", "datelabel", "param", "value", "mflag", "qflag", "sflag", "time"]
        if station_cols is None:
            station_cols = ["id", "latitude", "longitude", "elevation", "state", "name", "gsn_flag", "hcn_crn_flag",
                            "wmo_id"]

        self.db_name = db_name
        self.db_user = db_user
        self.db_password = db_password
        self.db_host = db_host
        self.db_port = db_port
        self.weather_cols = weather_cols
        self.station_cols = station_cols
        self.debug_messages = debug_messages

        # self.create_stations_table()

    def connect_to_db(self):
        """
        This creates a connection to the database. It then returns the connection and the cursor.

        :return: a connection and cursor for the database
        """
        try:
            connection = psycopg2.connect(
                dbname=self.db_name,
                user=self.db_user,
                password=self.db_password,
                host=self.db_host,
                port=self.db_port
            )
            cursor = connection.cursor()
            if self.debug_messages:
                print(f"Connected to database {self.db_name} with user {self.db_user}")
            return connection, cursor
        except Exception as error:
            print(f"Error: {error}")

    def insert_copy(self, file_path="", table_name="", columns=None):
        if columns is None:
            columns = []

        connection, cursor = self.connect_to_db()

        try:
            copy_command = sql.SQL("""
                COPY {table} ({columns}) FROM STDIN WITH CSV HEADER
            """).format(
                table=sql.Identifier(table_name),
                columns=sql.SQL(',').join(map(sql.Identifier, columns))
            )
            print(f"Copying file {file_path} to database {table_name}")
            with open(file_path, 'r') as file:
                cursor.copy_expert(copy_command, file)
            connection.commit()
            print(f"Insert with copy of file {file_path} to table: {table_name} done.")
            cursor.execute(f'SELECT COUNT(*) FROM "{table_name}"')
            row_count = cursor.fetchone()[0]
            print(f"Row count after insertion in table {table_name}: {row_count}")
        except Exception as error:
            print(f"Error: {error}")
            if connection:
                connection.rollback()
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
            if self.debug_messages:
                print(f"Disconnected")

    def create_stations_table(self):
        """
        This creates a station table with name "Station" in the database

        :return:
        """
        name = "Station"
        connection, cursor = self.connect_to_db()

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
            cursor.execute(create_table_command)
            connection.commit()
            print(f"{name} table created.")
        except Exception as error:
            print(f"Error: {error}")
            if connection:
                connection.rollback()
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
            if self.debug_messages:
                print(f"Disconnected")

    def create_climate_table(self, year):
        """
        This creates a table for the specified year with the name Climate{year}

        :param year: the year for which to create the table
        :return:
        """
        table_name = f"Climate{year}"
        station_table = "Station"

        connection, cursor = self.connect_to_db()

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
            cursor.execute(create_table_command)
            connection.commit()
            print(f"Table {table_name} created successfully.")
        except Exception as error:
            print(f"Error: {error}")
            if connection:
                connection.rollback()
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
            if self.debug_messages:
                print(f"Disconnected")

        return table_name
    
    def create_climate_tables(self, years=None):
        """
        This creates a table for the specified year with the name Climate{year}

        :param year: the year for which to create the table
        :return:
        """
        for year in years: 
            self.create_climate_table(year)
            
        return True

    def drop_table(self, table_name):
        """
        This drops a specified table from the database

        :param table_name: the table to drop
        :return:
        """
        connection, cursor = self.connect_to_db()

        try:
            drop_table_command = sql.SQL("DROP TABLE IF EXISTS {table}").format(table=sql.Identifier(table_name))
            cursor.execute(drop_table_command)
            connection.commit()
            print(f"Table {table_name} dropped successfully.")
        except Exception as error:
            print(f"Error: {error}")
            if connection:
                connection.rollback()
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
            if self.debug_messages:
                print(f"Disconnected")

    def count_rows(self, table_name):
        """
        This counts the number of rows in a specified table.

        :param table_name: The table to be checked
        :return:
        """
        connection, cursor = self.connect_to_db()

        try:
            count_command = sql.SQL('SELECT COUNT(*) FROM {table}').format(
                table=sql.Identifier(table_name)
            )
            cursor.execute(count_command)
            row_count = cursor.fetchone()[0]
            print(f"The table {table_name} contains {row_count} rows.")
        except Exception as error:
            print(f"Error: {error}")
            if connection:
                connection.rollback()
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
            if self.debug_messages:
                print(f"Disconnected")
        return row_count

    def split_csv_file(self, file_path, num_chunks):
        """
        This splits a file into a specified number of chunks. Each chunk has the same size

        :param file_path: The Path to the file to be split
        :param num_chunks: the number of chunks
        :return: returns an array of file paths to the chunks
        """

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
                print(
                    f"Writing chunk {chunk_number} file to {file_base}_chunk{chunk_number}{file_ext} with size {len(chunk_lines)}")
                chunk_file_path = f"{file_base}_chunk{chunk_number}{file_ext}"
                with open(chunk_file_path, 'w') as chunk_file:
                    chunk_file.write(header)
                    chunk_file.writelines(chunk_lines)
        return [f"{file_base}_chunk{chunk_number}{file_ext}" for chunk_number in range(chunk_number + 1)]

    def multi_threaded_insert(self, file_path, table_name=None, columns=None, num_threads=4):
        """
        This is a multi_threaded insert function. It Takes a file as input, and splits it into a number of chunks
        specified by num_threads. It then starts a thread for each chunk and inserts the data into the specified table.
        When a thread finishes it also deletes the chunk file.

        :param file_path: path to the file to be inserted
        :param table_name: name of the table to be inserted into
        :param columns: the columns of the table
        :param num_threads: number of chunks and threads to use
        :return:
        """
        if columns is None:
            columns = []

        if table_name is None:
            print(f"Error: table_name must be provided")
            return
        
        if self.count_rows(table_name=table_name) > 1:
            print(f"Data in table {table_name} already exists. Please check or delete the database before continuing.")
            return

        # this splits the file into equal sized chunks. That way one thread shouldn't finish that much earlier
        # than another, and we use resources efficiently
        chunks = self.split_csv_file(file_path, num_threads)

        def insert_chunk(chunk_file):
            # we use a specifically defined method so that it deletes the chunk
            # file at the end to clean up the data folder
            print(f'Thread started for chunk: {chunk_file}')
            try:
                connection, cursor = self.connect_to_db()

                copy_command = sql.SQL("""
                    COPY {table} ({columns}) FROM STDIN WITH CSV HEADER
                """).format(
                    table=sql.Identifier(table_name),
                    columns=sql.SQL(',').join(map(sql.Identifier, columns))
                )

                with open(chunk_file, 'r') as chunk:
                    # this adds the chunk to the database using copy statement
                    cursor.copy_expert(copy_command, chunk)
                connection.commit()
                print(f'Thread for chunk {chunk_file} completed.')
            except Exception as error:
                print(f"Error in thread: {error}")
                if connection:
                    connection.rollback()
            finally:
                if cursor:
                    cursor.close()
                if connection:
                    connection.close()
                # this removes the chunk file after we are finished with it
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

        return
    

    ###########################################################################
    # DATA CHECK 
    ###########################################################################

    def is_valid_year(self, year):
        """
        This function checks the passed year whether it is valid. It uses the parameterized years_in_db array to check if the passed year is included. 

        :param year: year as integer
        :return:
        """
        # TODO CHECK YEARS IN DATABASE WHEN APPLICATION IS LOADED?
        # if(int(year) in years_in_db):
        #     return True
        # else:
        #     return False
        return True
        
    
    def is_year_in_db(self, year):
        """
        This function checks the passed year whether there is data in the database for that year. If the table exists in the database, then it returns True, otherwise false.

        :param year: year as integer
        :return:
        """
        connection, cursor = self.connect_to_db()
        
        try:
            table_name = f'Climate{year}'

            # Construct the COUNT query using psycopg2.sql
            command = sql.SQL('''
                    SELECT COUNT(*)
                    FROM {table}   
            ''').format(
                table=sql.Identifier(table_name),
            )
            
            # Execute the SELECT query
            cursor.execute(command)
            result = cursor.fetchall()

            return len(result)>0

        except Exception as error:
            return False

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def check_year(self, year):
        """
        This function combines the both checks whether the year is in the class-defined years array and in the database.

        :param year: year as integer
        :return:
        """
        valid = self.is_valid_year(int(year))
        in_db = self.is_year_in_db(int(year))

        if valid and in_db:
            return True
        else:
            if self.debug_messages:
                print(f"Year {year} not in db and/or is not valid.")
            return False


    ###########################################################################
    # GET DATA 
    ###########################################################################

    def get_station_data_by_stationcode(self, columns, stationcode):
        """
        This function returns the station row of the 'Station' table with the passed stationcode.

        :param columns: return columns of the station table
        :param stationcode: The passed stationcode as string (e.g. 'AG000060390')
        :return:
        """
        # connect to database
        connection, cursor = self.connect_to_db()
        
        try:
            table_name = f'Station'

            # Construct the COUNT query using psycopg2.sql
            command = sql.SQL('''
                    SELECT {columns} 
                    FROM {table} 
                    WHERE id = {stationcode}               
            ''').format(
                columns=sql.SQL(', ').join(map(sql.Identifier, columns)),
                table=sql.Identifier(table_name),
                stationcode=sql.Identifier(stationcode),
            )

            if self.debug_messages:
                print(command.as_string(cursor.connection))
            
            # Execute the SELECT query
            cursor.execute(command)
            result = cursor.fetchall()

            data = pd.DataFrame(result, columns=columns)
                
            # Print the result specifications
            if self.debug_messages:
                print(f"The requested query returned {len(data)} results.")
                if len(data) == 1:
                    print(data)

        except Exception as error:
            print(f"Error: {error}")
            if connection:
                connection.rollback()

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
            if not data.empty:
                return data
            else:
                return pd.DataFrame(columns=columns)
            
    def get_station_data(self, columns):
        """
        This function returns all rows of the 'Station' table.

        :param columns: return columns of the station table
        :return:
        """
        # connect to database
        connection, cursor = self.connect_to_db()
        
        try:
            table_name = f'Station'

            # Construct the COUNT query using psycopg2.sql
            command = sql.SQL('''
                    SELECT {columns} 
                    FROM {table}               
            ''').format(
                columns=sql.SQL(', ').join(map(sql.Identifier, columns)),
                table=sql.Identifier(table_name),
            )

            if self.debug_messages:
                print(command.as_string(cursor.connection))
            
            # Execute the SELECT query
            cursor.execute(command)
            result = cursor.fetchall()

            data = pd.DataFrame(result, columns=columns)
                
            # Print the result specifications
            if self.debug_messages:
                print(f"The requested query returned {len(data)} results.")
                if len(data) == 1:
                    print(data)

        except Exception as error:
            print(f"Error: {error}")
            if connection:
                connection.rollback()

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

            print("Alles gucci bis her")
            if not data.empty:
                return data
            else:
                return pd.DataFrame(columns=columns)
            
    def get_data_by_station_param(self, years, station, parameters):
        """
        Retrieves data from the SQL database of the passed years, the passed station and passed parameters.

        :param years: years as integer array
        :param station: stationcode of one station
        :param parameters: parameters as string array of requested parameters
        
        :return: 
        """
        # connect to database
        connection, cursor = self.connect_to_db()
        
        try:
            data = pd.DataFrame()
            for year in years: 
                table_name = f'Climate{year}'
                
                parameters_sql_list = ",".join([f"'{parameter}'" for parameter in parameters])

                # Construct the COUNT query using psycopg2.sql
                command = sql.SQL('''
                        SELECT {columns} 
                        FROM {table}
                        WHERE stationcode IN ({stations}) AND 
                                param IN ({parameters}) AND
                                date_part('month', datelabel) = {month}
                        ORDER BY datelabel                
                ''').format(
                    columns=sql.SQL(', ').join(map(sql.Identifier, self.weather_cols)),
                    table=sql.Identifier(table_name),
                    station=sql.SQL(station),
                    parameters=sql.SQL(parameters_sql_list),
                )

                if self.debug_messages:
                    print(command.as_string(cursor.connection))
                
                # Execute the SELECT query
                cursor.execute(command)
                result = cursor.fetchall()

                result_data = pd.DataFrame(result, columns=self.weather_cols)

                data = pd.concat([data, result_data])
                
            # Print the result specifications
            if self.debug_messages:
                print(f"The requested query returned {len(data)} results.")
                if len(data) == 1:
                    print(data)

        except Exception as error:
            print(f"Error: {error}")
            if connection:
                connection.rollback()

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
            if not data.empty:
                return data
            else:
                return pd.DataFrame(columns=columns)
    
    
    
    def get_month_data(self, year, month, parameters, stations, columns):
        """
        Retrieves monthly data from the SQL database for comparison of different years.

        :return: 
        """
        # connect to database
        connection, cursor = self.connect_to_db()
        
        try:
            table_name = f'Climate{year}'

            stations_sql_list = ",".join([f"'{station}'" for station in stations])
            parameters_sql_list = ",".join([f"'{parameter}'" for parameter in parameters])

            # Construct the COUNT query using psycopg2.sql
            command = sql.SQL('''
                    SELECT {columns} 
                    FROM {table}
                    WHERE stationcode IN ({stations}) AND 
                            param IN ({parameters}) AND
                            date_part('month', datelabel) = {month}
                    ORDER BY datelabel                
            ''').format(
                columns=sql.SQL(', ').join(map(sql.Identifier, columns)),
                table=sql.Identifier(table_name),
                stations=sql.SQL(stations_sql_list),
                parameters=sql.SQL(parameters_sql_list),
                month=sql.SQL(str(month))
            )

            if self.debug_messages:
                print(command.as_string(cursor.connection))
            
            # Execute the SELECT query
            cursor.execute(command)
            result = cursor.fetchall()

            data = pd.DataFrame(result, columns=columns)
                
            # Print the result specifications
            if self.debug_messages:
                print(f"The requested query returned {len(data)} results.")
                if len(data) == 1:
                    print(data)

        except Exception as error:
            print(f"Error: {error}")
            if connection:
                connection.rollback()

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
                
            if not data.empty:
                return data
            else:
                return pd.DataFrame(columns=columns)

    def get_data_between_dates_one_year(self, year, start_date, end_date, parameters, stations, columns):
        """
        Retrieves data from the SQL database.
            
        :param year: 
        :param columns: 
        :param condition: 

        :return: 
        """
        # connect to database
        connection, cursor = self.connect_to_db()
        
        try:
            table_name = f'Climate{year}'

            stations_sql_list = ",".join([f"'{station}'" for station in stations])
            parameters_sql_list = ",".join([f"'{parameter}'" for parameter in parameters])

            # Construct the COUNT query using psycopg2.sql
            command = sql.SQL('''
                    SELECT {columns} 
                    FROM {table}
                    WHERE stationcode IN ({stations}) AND 
                            param IN ({parameters})
                    ORDER BY datelabel                
            ''').format(
                columns=sql.SQL(', ').join(map(sql.Identifier, columns)),
                table=sql.Identifier(table_name),
                stations=sql.SQL(stations_sql_list),
                parameters=sql.SQL(parameters_sql_list),
            )

            # if self.debug_messages:
            print(command.as_string(cursor.connection))
            
            # Execute the SELECT query
            cursor.execute(command)
            result = cursor.fetchall()

            
            data = pd.DataFrame(result, columns=columns)
                
            # Print the result specifications
            if self.debug_messages:
                print(f"The requested query returned {len(data)} results.")
                if len(data) == 1:
                    print(data)

        except Exception as error:
            print(f"Error: {error}")
            if connection:
                connection.rollback()

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
            if not data.empty:
                return data
            else:
                return pd.DataFrame(columns=columns)
            
    def get_data_between_dates(self, start_date, end_date, parameters, stations, columns):
        """
        Retrieves data from the SQL database.
        
        :return: 
        """
        try:
            start_year = start_date[:4]
            end_year = end_date[:4]
            
            if start_year == end_year and self.check_year(start_year):
                data = self.get_data_between_dates_one_year(start_year, start_date, end_date, parameters, stations, columns)
            else: 
                years_to_process = np.arange(int(start_year), int(end_year)+1, 1)

                filtered_years = [year for year in years_to_process if self.check_year(start_year)]

                data = pd.DataFrame()
                for year in filtered_years:
                    new = self.get_data_between_dates_one_year(year, start_date, end_date, parameters, stations, columns)
                    data = pd.concat([data, new])

        except Exception as error:
            print(f"Error: {error}")
            
        finally:
            if not data.empty:
                return data
            else:
                return pd.DataFrame(columns=columns)

    def get_data_yearly(self, years, parameters, stations, columns):
        """
        Retrieves data from the SQL database.
        
        :return: 
        """
        try:

            filtered_years = [year for year in years if self.check_year(year)]

            data = pd.DataFrame()
            for year in filtered_years:
                new = self.get_data_between_dates_one_year(year, f"{year}-01-01", f"{year}-12-31", parameters, stations, columns)
                data = pd.concat([data, new])

        except Exception as error:
            print(f"Error: {error}")
            
        finally:
            if not data.empty:
                return data
            else:
                return pd.DataFrame(columns=columns)
