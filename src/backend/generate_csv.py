import sqlite3
import csv
import pandas as pd

# Read Excel file and insert data into the table
districts_year_df = pd.read_excel('data/SchoolDistricts.xlsx', sheet_name='Data')
districts_loc_df = pd.read_excel('data/SchoolDistrictsLocation.xlsx')

clean_districts_year_df = districts_year_df[['leaid', 'district', 'ppcstot', 'predcost', 'fundinggap', 'outcomegap', 'enroll', 'year', 'state_name']]
clean_districts_loc_df = districts_loc_df[['LEAID', 'CITY', 'LAT', 'LON']]

print(clean_districts_year_df.head())
print(clean_districts_loc_df.head())

conn = sqlite3.connect('example.db')
cursor = conn.cursor()

cursor.execute('''
    DROP TABLE IF EXISTS DistrictsYear;
    ''')

cursor.execute('''
    DROP TABLE IF EXISTS DistrictsLocation;
    ''')

cursor.execute('''CREATE TABLE DistrictsYear (
                    leaid INTEGER,
                    district TEXT,
                    ppcstot INTEGER,
                    predcost INTEGER,
                    fundinggap INTEGER,
                    outcomegap INTEGER,
                    enroll INTEGER,
                    year INTEGER,
                    state_name TEXT
                 )''')

cursor.execute('''CREATE TABLE DistrictsLocation (
                    LEAID INTEGER,
                    CITY TEXT,
                    LAT INTEGER,
                    LON INTEGER
                 )''')

# insert into DistrictYear table
for row in clean_districts_year_df.itertuples(index=False):
    cursor.execute('''
        INSERT INTO DistrictsYear
        (leaid, district, ppcstot, predcost, fundinggap, outcomegap, enroll, year, state_name)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', 
        row)

# insert into DistrictLocation table
for row in clean_districts_loc_df.itertuples(index=False):
    cursor.execute('''
        INSERT INTO DistrictsLocation
        (LEAID, CITY, LAT, LON)
        VALUES (?, ?, ?, ?)
        ''', 
        row)     

cursor.execute('''
    DROP VIEW IF EXISTS Districts
    ''')

#Join two tables on leadid
cursor.execute('''
    CREATE VIEW Districts AS 
        SELECT 
            y.leaid,
            year,
            district, 
            CITY as city, 
            state_name,
            LAT as lat, 
            LON as lon,
            ppcstot,
            predcost,
            fundinggap,
            outcomegap,
            enroll
        FROM
        DistrictsLocation l JOIN DistrictsYear y ON l.LEAID = y.leaid
        ''')

cursor.execute('''SELECT * FROM Districts''')
rows = cursor.fetchall()
with open('data/dataset_by_year.csv', 'w', newline='') as csvfile:
    csv_writer = csv.writer(csvfile)
    csv_writer.writerow([i[0] for i in cursor.description])
    csv_writer.writerows(rows)

cursor.execute('''
    SELECT 
        leaid, district, city, state_name, lat, lon,
        AVG(ppcstot) AS ppcstot,
        AVG(predcost) AS predcost,
        AVG(fundinggap) AS fundinggap,
        AVG(outcomegap) AS outcomegap,
        AVG(enroll) AS enroll
    FROM
    Districts
    GROUP BY leaid, district, city, state_name, lat, lon
    ''')

rows = cursor.fetchall()
with open('data/dataset_by_avgs.csv', 'w', newline='') as csvfile:
    csv_writer = csv.writer(csvfile)
    csv_writer.writerow([i[0] for i in cursor.description])
    csv_writer.writerows(rows)

cursor.execute('''
    SELECT 
        year,
        AVG(ppcstot) AS ppcstot,
        AVG(predcost) AS predcost,
        AVG(fundinggap) AS fundinggap,
        AVG(outcomegap) AS outcomegap,
        AVG(enroll) AS enroll
    FROM
    Districts
    GROUP BY year
    ''')
rows = cursor.fetchall()
with open('data/avg_by_year.csv', 'w', newline='') as csvfile:
    csv_writer = csv.writer(csvfile)
    csv_writer.writerow([i[0] for i in cursor.description])
    csv_writer.writerows(rows)

# Commit changes and close connection
conn.commit()
conn.close()
