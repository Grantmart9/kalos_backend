####################################
from flask_cors import CORS
from flask import Flask, request, jsonify
import psycopg2
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

if __name__ == '__main__':
    app.run(port=5002)
