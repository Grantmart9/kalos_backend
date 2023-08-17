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
period = 20

while t <= 10:
    Current_time_datetime = datetime.now()
    current_hour = Current_time_datetime.hour
    current_sec = Current_time_datetime.second
    current_min = Current_time_datetime.minute
    delete_sec = current_sec - period
    ## Initialise connection ##
    conn = psycopg2.connect(host=host, database=database,
                            user=user, password=passphrase)

    ## Cursor class is used to execute queries ##
    cur = conn.cursor()
    
    ## SQL query ##
    cur.execute('SELECT user_id FROM user_otp WHERE stamp_sec <= %s OR stamp_min < %s',(delete_sec,current_min,))

    user_data = cur.fetchone()
    
    if user_data is not None:
        conn = psycopg2.connect(host=host, database=database,
                            user=user, password=passphrase)
        user1 = str(user_data)
        user2 = user1.replace('(','')
        user3 = user2.replace(')','')
        user4 = user3.replace(',','')
        user5 = user4.rstrip("'")
        user6 = user5.lstrip("'")
        ## Cursor class is used to execute queries ##
        cur = conn.cursor()
        ## SQL query ##
        cur.execute('DELETE FROM user_otp WHERE user_id = %s',(user6,))
        conn.commit()
        ## Close cursor ##
        cur.close()
        print("TimeStamp: " + str(current_hour)+ ":" + str(current_min)+ ":" + str(current_sec) + " - Token For User: " + user6 + " Was DELETED")
    if user_data is None:
        print("TimeStamp: " +str(current_hour)+ ":" + str(current_min)+ ":" + str(current_sec))
    
    time.sleep(0.5)


