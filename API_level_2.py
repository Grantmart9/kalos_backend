####################################
from flask_cors import CORS
from flask import Flask, request, jsonify
import psycopg2
import secrets
from datetime import datetime
####################################
## DB credentials ##
####################################
host = "localhost"
database = "postgres"
user = "postgres"
passphrase = "Xiobh@nmart10"
####################################
app = Flask(__name__)
CORS(app)
app.debug = True
#####################################
### Require OTP #####################
#####################################

@app.route('/put_order_auth', methods=['POST'])
def put_order_auth():
    conn = None
    incoming_data = request.json
    token = request.headers['token']
    user_id = incoming_data['user_id']
    Current_time_datetime = datetime.now()
    ## Get min ##
    current_min = Current_time_datetime.minute
    current_sec = Current_time_datetime.second
   
    try:
        conn = psycopg2.connect(host=host, database=database,
                                user=user, password=passphrase)
        ## Connect ##
        cur = conn.cursor()
        ## Check if jwt exists in DB ##
        cur.execute("SELECT * FROM user_token WHERE jwt = %s", (str(token),))
        jwt_token = cur.fetchone()
        if jwt_token is not None:
            ## Connect ##
            # 1) Check if OTP exists for user_id
            cur.execute("SELECT * FROM user_otp WHERE user_id = %s", (user_id,))
            entry = cur.fetchone()
            # 2) If not exist, create new OTP and store New OTP in DB
            if entry is None:
                otp = secrets.token_hex(6)
                cur.execute("INSERT INTO user_otp (user_id, otp, stamp_min,stamp_sec) VALUES(%s,%s,%s,%s)",
                            (user_id, otp, current_min,current_sec))
                ## Commit the request ##
                conn.commit()
                ## Close cursor ##
                cur.close()
                ## Close connection ##
                conn.close()
                # 1) Check if OTP exists for user_id
                #cur.execute("SELECT cell,order_id, FROM user_data WHERE user_id = %s", (user_id,))
                #user_data = cur.fetchone()
                #print(str(user_data))
            # 2) If exists, copy OTP out of DB.  
            if entry is not None:
                print("OTP already exists")
            # 3) Send OTP, cell and order_id to SNS topic.
            print("sending OTP to:" + str(otp) + " for order ID: " )
        if jwt_token is None:
            print("User not authorise")
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error while quering DB")
        print(error)
    finally:
        if conn is not None:
            conn.close()

    return ("Sending OTP to : ")

@app.route('/put_order', methods=['POST'])
def put_order():
    conn = None
    incoming_data = request.json
    token = request.headers['token']
    cart = incoming_data['cart']
    user_id = incoming_data['user_id']
    try:
        conn = psycopg2.connect(host=host, database=database,
                                user=user, password=passphrase)
        ## Connect ##
        cur = conn.cursor()
        ## Check if jwt exists in DB ##
        cur.execute("SELECT * FROM user_token WHERE jwt = %s", (str(token),))
        jwt_token = cur.fetchone()
        ## after token check we do OTP check ##
        if jwt_token is not None:
            ## Connect ##
            print({"user_id":user_id,"cart":cart})
        if jwt_token is None:
            print("User not authorise")
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error while quering DB")
        print(error)
    finally:
        if conn is not None:
            conn.close()

    return ("Put order")

@app.route('/update_user', methods=['POST'])
def update_user():
    conn = None
    incoming_data = request.json
    token = request.headers['token']
    cart = incoming_data['cart']
    user_id = incoming_data['user_id']
    try:
        conn = psycopg2.connect(host=host, database=database,
                                user=user, password=passphrase)
        ## Connect ##
        cur = conn.cursor()
        ## Check if jwt exists in DB ##
        cur.execute("SELECT * FROM user_token WHERE jwt = %s", (str(token),))
        jwt_token = cur.fetchone()
        ## after token check we do OTP check ##
        if jwt_token is not None:
            ## Connect ##
            print({"user_id":user_id,"cart":cart})
        if jwt_token is None:
            print("User not authorise")
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error while quering DB")
        print(error)
    finally:
        if conn is not None:
            conn.close()

    return ("Changing user details")


if __name__ == '__main__':
    app.run(port=5003)