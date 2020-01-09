from pprint import pprint

import httplib2
import googleapiclient.discovery
from oauth2client.service_account import ServiceAccountCredentials


# Файл, полученный в Google Developer Console
CREDENTIALS_FILE = 'creds.json'
# ID Google Sheets документа (можно взять из его URL)

spreadsheet_id = '1mknLUZzGEtwyU2DkkRAqVXUtAOk6JoJ0s8u83WJ5ItA'

# Авторизуемся и получаем service — экземпляр доступа к API
credentials = ServiceAccountCredentials.from_json_keyfile_name(
    CREDENTIALS_FILE,
    ['https://www.googleapis.com/auth/spreadsheets',
     'https://www.googleapis.com/auth/drive'])
httpAuth = credentials.authorize(httplib2.Http())
service = googleapiclient.discovery.build('sheets', 'v4', http = httpAuth)
values = {}
# Пример чтения файла
values = service.spreadsheets().values().get(
    spreadsheetId=spreadsheet_id,
    range='A2:L64',
    majorDimension='ROWS'
).execute()

#pprint(values)
#print(values['values'][1][0])


from mysql.connector import MySQLConnection, Error
from db_config import read_db_config

dbconfig = read_db_config()

anime = "anime"
anime_genres = "anime_genres"
genre = "genre"
anime_producers = "anime_producers"
producer = "producer"

anime_args = ['title', 'poster_link', 'type', 'description', 'review', 'watch_link', 'year', 'storyline_rate', 'artwork_rate', 'ost_rate']
"""
0 title
1 poster_link
2 type
3 description
4 review
5 watch_link
6 year
7 storyline_rate
8 artwork_rate
9 ost_rate
"""

insert_args = ''
for i in anime_args:
    insert_args += i + ', '
insert_args = insert_args[:-2]


def insert():
    insert_request = "INSERT INTO " + anime + " (" + insert_args + ") VALUES "
    #тут я проверяю через индекс столбца его тип данных <=> первые 6 столбцов типа varchar/text, поэтому при инсерте, в значениях мы должны указывать их с ковычками
    for row_args in values['values']:
        i = 0
        insert_request += "("
        for arg in row_args:
            if(i<6):
                arg = arg.replace('"', '``')
                arg = arg.replace("'", '`')
                insert_request += '"' + arg + '"' + ', '
            else:
                if(i<10):
                    insert_request += arg + ', '
                else:
                    insert_request = insert_request[:-2] + ')'
                    cursor.execute(insert_request)
                    insert_request = "INSERT INTO " + anime + " (" + insert_args + ") VALUES "
                    cursor.execute("SELECT LAST_INSERT_ID()")
                    anime_id = cursor.fetchone()[0]
                    arg_genres = row_args[i].split(', ')
                    for j in arg_genres:
                        print(j, 1)
                        strj = '"' + str(j) + '"'
                        cursor.execute("SELECT COUNT(title) FROM " + genre + " WHERE title = " + strj)
                        if cursor.fetchone()[0] == 0:
                            print("INSERT INTO " + genre + " (title) VALUES (" + strj + ")")
                            cursor.execute("INSERT INTO " + genre + " (title) VALUES (" + strj + ")")
                           
                            cursor.execute("SELECT LAST_INSERT_ID()")
                        else:
                            cursor.execute("SELECT id FROM " + genre + " WHERE title = " + strj)
                        genre_id = cursor.fetchone()[0]
                        cursor.execute("INSERT INTO " + anime_genres + " (genre_id, anime_id) VALUES (" + str(genre_id) + ", " + str(anime_id) + ")")
                    arg_producers = row_args[i+1].split(', ')
                    for j in arg_producers:
                        strj = '"' + str(j) + '"'
                        cursor.execute("SELECT COUNT(title) FROM " + producer + " WHERE title = " + strj)
                        if cursor.fetchone()[0] == 0:
                            cursor.execute("INSERT INTO " + producer + " (title) VALUES (" + strj + ")")
                            cursor.execute("SELECT LAST_INSERT_ID()")
                        else:
                            cursor.execute("SELECT id FROM " + producer + " WHERE title = " + strj)
                        producer_id = cursor.fetchone()[0]
                        cursor.execute("INSERT INTO " + anime_producers + " (producer_id, anime_id) VALUES (" + str(producer_id) + ", " + str(anime_id) + ")")
                    break
            i+=1

try:
    conn = MySQLConnection(**dbconfig)
    cursor = conn.cursor()
    insert()
    conn.commit()
except Error as e:
    print(e)
finally:
    cursor.close()
    conn.close()
