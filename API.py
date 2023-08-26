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
            cost = product[6]
            qty =product[5]
            items.append({"product_description": product_description, 
"product_id": product_id,
                        "brand": brand, "categor": category, "qty": 
qty,"cost":cost})
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error while quering DB")
        print(error)
    finally:
        if conn is not None:
            conn.close()
    return (jsonify(items))

####################################
## JWT required requests ###########
####################################
## Get Cart ##
####################################
@app.route('/get_cart', methods=['GET'])
def get_cart():
    conn = None
    message = "None"
    Data = request.json
    token = request.headers['token']
    cart_id = Data['cartid']
    try:
        ## configure connection paramters ##
        conn = psycopg2.connect(host=host, database=database,
                                user=user, password=passphrase)
        ## Connect ##
        cur = conn.cursor()
        ## Check if jwt exists in DB ##
        cur.execute("SELECT * FROM user_token WHERE jwt = %s", (str(token),))
        jwt_token = cur.fetchone()
        if jwt_token is not None:
            cur.execute("SELECT * FROM carts WHERE cartid = %s", (cart_id,))
            returned_cart = cur.fetchall()
            full_cart = []
            for item in returned_cart:
                product_description = item[2]
                product_id = item[3]
                brand = item[4]
                delivery_time = item[5]
                qty = item[6]
                full_cart.append({"product_description": product_description,
                                 "product_id": product_id, "brand": brand, "delivery_time": int(delivery_time), "qty": int(qty)})
            message = full_cart
        if jwt_token is None:
            message = "user not authorised"

    except (Exception, psycopg2.DatabaseError) as error:
        print("Error while quering DB: "+str(error))
    finally:
        if conn is not None:
            conn.close()

    return message
#####################################
## Add To Cart ##
#####################################


@app.route('/add_to_cart', methods=['POST'])
def put_cart():
    conn = None
    message = "None"
    Data = request.json
    token = request.headers['token']
    cart_id = Data['cartid']
    items = Data['items']
    try:
        ## configure connection paramters ##
        conn = psycopg2.connect(host=host, database=database,
                                user=user, password=passphrase)
        ## Connect ##
        cur = conn.cursor()
        ## Check if jwt exists in DB ##
        cur.execute("SELECT * FROM user_token WHERE jwt = %s", (str(token),))
        jwt_token = cur.fetchone()
        if jwt_token is not None:
            ## Check if product_id and cartid combo exisists in DB ##
            cur.execute("SELECT * FROM carts WHERE product_id = %s AND cartid = %s",
                        (str(items['product_id']), cart_id,))
            entry = cur.fetchone()
            # If it exisits meaning products = 0
            if entry is not None:
                message = "product exisists"
                cur_qty = int(entry[6])
                add_qty = int(items['qty'])
                new_qty = cur_qty + add_qty
                cur.execute("UPDATE carts SET qty = %s WHERE product_id = %s AND cartid = %s", (str(
                    new_qty), str(items['product_id']), cart_id,))
                conn.commit()
                cur.execute(
                    "SELECT * FROM carts WHERE cartid = %s", (cart_id,))
                returned_cart = cur.fetchall()
                full_cart = []
                for item in returned_cart:
                    product_description = item[2]
                    product_id = item[3]
                    brand = item[4]
                    delivery_time = item[5]
                    qty = item[6]
                    full_cart.append({"product_description": product_description,
                                      "product_id": product_id, "brand": brand, "delivery_time": int(delivery_time), "qty": int(qty)})
                    message = full_cart
                    cur.close()
                    conn.close()
                ## Remember to return updated tuple ##
            if entry is None:
                try:
                    cur.execute("INSERT INTO carts (cartid,product_description,product_id,brand,delivery_time,qty) VALUES(%s,%s,%s,%s,%s,%s)", (int(cart_id),
                                items['product_description'], items['product_id'], items['brand'], int(items['delivery_time']), int(items['qty']),))
                    conn.commit()
                    cur.close()
                    conn.close()
                    message = "item added"
                except (Exception, psycopg2.DatabaseError) as error:
                    print("Error while quering DB: "+str(error))
                finally:
                    if conn is not None:
                        conn.close()
        if jwt_token is None:
            message = "User not authorised"
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error while quering DB: " + str(error))
    finally:
        if conn is not None:
            conn.close()

    return message
#####################################
## Order data ##
#####################################

@app.route('/get_order', methods=['GET'])
def get_order():
    conn = None
    token = request.headers['token']
    try:
        conn = psycopg2.connect(host=host, database=database,
                                user=user, password=passphrase)
        ## Connect ##
        cur = conn.cursor()
        ## Check if jwt exists in DB ##
        cur.execute("SELECT * FROM user_token WHERE jwt = %s", (str(token),))
        jwt_token = cur.fetchone()
        if jwt_token is not None:
            print("user authorised")
        if jwt_token is None:
            print("User not authorise")
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error while quering DB")
        print(error)
    finally:
        if conn is not None:
            conn.close()

    return ("get order")
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
    app.run(port=5000)
