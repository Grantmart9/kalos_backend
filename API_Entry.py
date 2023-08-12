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
####################################
## User Authentication ##
####################################


@app.route('/auth', methods=['GET'])
def users():
    conn = None
    Data = request.json
    json_Data = Data['user_details']
    username = json_Data['username']
    userpassword = json_Data['password']
    try:
        ## Initialise connection ##
        conn = psycopg2.connect(host=host, database=database,
                                user=user, password=passphrase)
        ## Cursor class is used to execute queries ##
        cur = conn.cursor()
        ## Query string ##
        query_string = 'SELECT * FROM user_data WHERE username=%s and password=%s'
        ## SQL query ##
        cur.execute(query_string, (username, userpassword))
        ## Execute cur and fetch the row ##
        user_data = cur.fetchone()
        ## if user_data returns not None deny access ##
        if user_data is not None:
            ### First we need to search DB if JWT exists for this session ##
            query_string = 'SELECT * FROM user_token WHERE username=%s'
            ## SQL query ##
            cur.execute(query_string, (username,))
            ## Execute cur and fetch the row ##
            user_token = cur.fetchone()
            if user_token is None:
                ## Generate JWT ##
                jwt = secrets.token_hex(32)
                ## get current time ##
                Current_time_datetime = datetime.now()
                ## Get min ##
                current_min = Current_time_datetime.minute
                current_hour = Current_time_datetime.hour
                ## Return JWT in body ##
                con = {"JWT": jwt}
                ## Insert new token if none exist ##
                cur.execute("INSERT INTO user_token (username, jwt, stamp_min,stamp_hour) VALUES(%s,%s,%s,%s)",
                            (username, jwt, current_min, current_hour))
                ## Commit the request ##
                conn.commit()
                ## Close cursor ##
                cur.close()
                ## Close connection ##
                conn.close()
            if user_token is not None:
                ## Initialise connection ##
                conn = psycopg2.connect(host=host, database=database,
                                        user=user, password=passphrase)
                ## Cursor class is used to execute queries ##
                cur = conn.cursor()
                ## SQL query ##
                cur.execute(
                    'SELECT jwt FROM user_token WHERE username = %s', (username,))
                jwt_exist = str(cur.fetchone())
                token1 = jwt_exist
                token2 = token1.replace('(', '')
                token3 = token2.replace(')', '')
                token4 = token3.replace(',', '')
                token5 = token4.rstrip("'")
                token6 = token5.lstrip("'")
                ## Commit the request ##
                conn.commit()
                ## Close cursor ##
                cur.close()
                ## Close connection ##
                conn.close()
                con = {"JWT": token6}
        ## If no data returned from sql query ##
        if user_data is None:
            con = "Invalid username or password"
    ## If can't establish connection with DB ##
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error while querying DB" + str(error))
    finally:
        if conn is not None:
            ## Close cursor ##
            cur.close()
            ## Close connection ##
            conn.close()
    return (jsonify(con))
###################################
## Add new User ##
###################################


@app.route('/put_users', methods=['POST'])
def put_users():
    conn = None
    message = None
    incoming_data = request.json
    username = incoming_data['username']
    password = incoming_data["password"]
    firstname = incoming_data["firstname"]
    lastname = incoming_data["lastname"]
    address = incoming_data["address"]
    email = incoming_data["email"]
    cell = incoming_data["cell"]
    order_id = 0
    try:
        ## configure connection paramters ##
        conn = psycopg2.connect(host=host, database=database,
                                user=user, password=passphrase)
        ## Connect ##
        cur = conn.cursor()
        ## Check if username and email already exists in DB ##
        cur.execute(
            "SELECT * FROM user_data WHERE email = %s OR username = %s", (email, username,))
        user_data = cur.fetchone()
        if user_data is None:
            ## Execute the query ##
            cur.execute("INSERT INTO user_data (username, password, address, firstname, lastname,order_id,email,cell) VALUES(%s, %s,%s, %s,%s,%s,%s,%s)",
                        (username, password, address, firstname, lastname, order_id, email, cell))
            conn.commit()
            message = "New User Created"
            cur.close()
            conn.close()
        if user_data is not None:
            message = "User with email address: " + email + " already exisits"
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error while quering DB")
        print(error)
    finally:
        if conn is not None:
            conn.close()
    return (message)
###################################
## Get products ##
###################################


@app.route('/get_products', methods=['GET'])
def get_products():
    conn = None
    try:
        ## configure connection paramters ##
        conn = psycopg2.connect(host=host, database=database,
                                user=user, password=passphrase)
        ## Connect ##
        cur = conn.cursor()
        ## Check if username and email already exists in DB ##
        cur.execute(
            "SELECT * FROM products ")
        user_data = cur.fetchall()
        items = []
        for product in user_data:
            product_description = product[1]
            product_id = product[2]
            brand = product[3]
            category = product[4]
            qty = product[5]
            items.append({"product_description": product_description, "product_id": product_id,
                        "brand": brand, "categor": category, "qty": qty})
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error while quering DB")
        print(error)
    finally:
        if conn is not None:
            conn.close()
    return (jsonify(items))

if __name__ == '__main__':
    app.run(port=5001)
