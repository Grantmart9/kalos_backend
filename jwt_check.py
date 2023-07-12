####################################
import psycopg2
import time
from datetime import datetime
## DB credentials ##################
host = "localhost"
database = "postgres"
user = "postgres"
passphrase = "Xiobh@nmart10"
####################################
t = 0
period = 5
hours = 1

while t <= 10:
    Current_time_datetime = datetime.now()
    current_min = Current_time_datetime.minute
    delete_hour = Current_time_datetime.hour
    delete_time = current_min - period
    delete_min = str(delete_time)

    ## Initialise connection ##
    conn = psycopg2.connect(host=host, database=database,
                            user=user, password=passphrase)

    ## Cursor class is used to execute queries ##
    cur = conn.cursor()

    ## SQL query ##
    cur.execute('SELECT username FROM user_token WHERE stamp_min <= %s OR stamp_hour >%s',(delete_min,delete_hour))

    user_data = str(cur.fetchone())
    conn.commit()
    ## Close cursor ##
    cur.close()
    user1 = user_data
    user2 = user1.replace('(','')
    user3 = user2.replace(')','')
    user4 = user3.replace(',','')
    user5 = user4.rstrip("'")
    user6 = user5.lstrip("'")

    if user_data != None:
        conn = psycopg2.connect(host=host, database=database,
                            user=user, password=passphrase)
        print(user6)
        ## Cursor class is used to execute queries ##
        cur = conn.cursor()
        ## SQL query ##
        cur.execute('DELETE FROM user_token WHERE username = %s',(user6,))
        conn.commit()
        ## Close cursor ##
        cur.close()

    time.sleep(0.001)


