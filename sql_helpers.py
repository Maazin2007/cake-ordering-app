import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from email_validator import EmailNotValidError, validate_email
from flask import session, redirect, url_for, flash
from functools import wraps

def get_db():
    conn = sqlite3.connect("bakery.db")
    conn.row_factory = sqlite3.Row
    return conn

def check_item(id):
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
                   SELECT id FROM items
                   """)
    rows = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    counter = 0
    for row in rows: 
        if row["id"] == id:
            counter += 1
    
    return False if counter == 0  else True

def get_cart(cart_dict):
    conn = get_db()
    cursor = conn.cursor()
    
    for key in cart_dict:
        cursor.execute("""
                       SELECT *
                       FROM items
                       WHERE id = ?
                       """, (int(key),))
        row = cursor.fetchone()
        if row:
            cart_dict[key].update(dict(row))  # Safe conversion

    cursor.close()
    conn.close()
    
    return cart_dict

def get_item_price(id):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
                   SELECT price 
                   FROM items 
                   WHERE id = ?
                   """,(id, ))
    row = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    return row["price"]

def get_total_price_cart(cart):
    return sum(cart[id]["price"] * cart[id]["amount"] for id in cart)

def place_order(cart, id):
    conn = get_db()
    cursor = conn.cursor()
    
    total_price = get_total_price_cart(cart)
    
    try:
        cursor.execute("""
                    INSERT INTO orders
                    (user_id, total_price, status)
                    VALUES (?, ?, "baking")
                    """, (id, total_price,))
        
        # gets the primary key of the last row inserted by cursor 
        order_id = cursor.lastrowid
        
        for item_id in cart:
            cursor.execute("""
                        INSERT INTO order_items
                        (order_id, item_id, item_quantity)
                        VALUES (?, ?, ?)
                        """,(order_id, cart[item_id]["id"], cart[item_id]["amount"],))
        
        conn.commit()
        
    except Exception as e:
        print("error adding order to db" + str(e))
        conn.rollback()
        
    finally:   
        cursor.close()
        conn.close()
    
def get_orders(user_id):
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # Step 1: Get all order IDs for the user
        cursor.execute("""
            SELECT id 
            FROM orders
            WHERE user_id = ?
        """, (user_id,))
        user_order_rows = cursor.fetchall()
        
        orders_list = [row["id"] for row in user_order_rows][::-1]  # Reversed list
        
        orders = {}
        
        for order_id in orders_list:
            # Step 2: Get order metadata (total_price, time)
            cursor.execute("""
                SELECT total_price, order_time, status
                FROM orders
                WHERE id = ?
            """, (order_id,))
            row = cursor.fetchone()
            
            orders[order_id] = {
                "value": row["total_price"],
                "time": row["order_time"],
                "status": row["status"],
                "items": {}  # initialize items dictionary here
            }

            # Step 3: Get items in the order
            cursor.execute("""
                SELECT items.id, order_items.item_quantity AS amount, items.name
                FROM items
                JOIN order_items ON items.id = order_items.item_id 
                WHERE order_items.order_id = ?
            """, (order_id,))
            rows = cursor.fetchall()
            
            for item in rows:
                orders[order_id]["items"][item["id"]] = {
                    "quantity": item["amount"],
                    "name": item["name"]
                }

        return orders

    except Exception as e:
        print("Error while handling database:", e)
        conn.rollback()
        return {}

    finally:
        cursor.close()
        conn.close()
        
def update_order(status, order_id, user_id):
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
                    UPDATE orders
                    SET status = ?
                    WHERE id = ?
                    AND user_id = ?
                    """, (status, order_id, user_id,))
        
        conn.commit()
        
    except Exception as e:
        print("error adding order to db" + str(e))
        conn.rollback()  
        
        raise Exception("error while trying to write to the database")
    
    finally:
        cursor.close()
        conn.close()
        
    
    
def get_orders_admin():
    # establishing connection with the database
    conn = get_db()
    cursor = conn.cursor()
    
    # safely accessing the data in the database
    try:
        # create empty list for list of id's
        list_id = []
        
        # get the execution from the list_id
        cursor.execute("""
                       SELECT id
                       FROM orders
                       WHERE status != 'Collected'
                       """)
        rows = cursor.fetchall()
        
        # getting list of all order id's 
        for row in rows:
            list_id.insert(0, row['id'])
            
        # creating empty dictonary to store all the orders
        admin_orders = {}
        # looping over each id in the list 
        for id in list_id:
            # putting the dictionary against the id
            admin_orders[id] = {}
            
            cursor.execute("""
                           SELECT user_id, total_price, order_time, status
                           FROM orders
                           WHERE id = ?
                           """, (id,))
            rows = cursor.fetchone()
            
            for key in rows.keys():
                admin_orders[id][key] = rows[key]
            
            cursor.execute("""
                           SELECT name
                           FROM people 
                           WHERE id=?
                           """, (rows["user_id"],))
            row = cursor.fetchone()
            admin_orders[id]["name"] = row["name"]
            
            # adding the items dictionary against the key
            admin_orders[id]["stuff"] = {}
            
            
        # adding the items to dictionary
        for key in admin_orders:
            
            cursor.execute("""
                SELECT items.id, order_items.item_quantity AS amount, items.name
                FROM items
                JOIN order_items ON items.id = order_items.item_id 
                WHERE order_items.order_id = ?
            """, (key,))
            rows = cursor.fetchall()
            
            for row in rows:
                admin_orders[key]["stuff"][row["id"]] = {
                    "quantity": row["amount"],
                    "name": row["name"]
                }
        
        return admin_orders
        
    except Exception as e:
        print("ERROR: ", e)
        conn.rollback()
        raise Exception("there was an issue accessing the database for getting admin orders")
    
    finally:
        cursor.close()
        conn.close()
        
def get_total_revenue():
    # establish connection with the database
    conn = get_db()
    cursor = conn.cursor()
    
    # create empty list of the revenue
    revenue_list = []
    
    # access the darabase safely and store each order revenue list
    try: 
        cursor.execute("""
                       SELECT total_price
                       FROM orders
                       WHERE status = 'Collected'
                       AND order_time >= datetime('now', '-1 month')
                       """)
        rows = cursor.fetchall()
        
        for row in rows:
            revenue_list.append(row["total_price"])
            
    except Exception as e:
        print(str(e))
        print("issue accessing the orders table to retrienve revenue")
        conn.rollback()
        raise Exception("issue accessing database")
        
    finally:
        cursor.close()
        conn.close()   
        
        return sum(revenue_list)
    
def get_total_cost():
    # establishing connection with the database
    conn = get_db()
    cursor = conn.cursor()
    total_monthy_cost = 0
    
    # safely running sql query
    try:
        cursor.execute("""
                        SELECT 
                        SUM(order_items.item_quantity * items.production_cost) AS cost
                        FROM order_items
                        JOIN items ON order_items.item_id = items.id
                        JOIN orders ON order_items.order_id = orders.id
                        WHERE orders.order_time >= datetime('now', '-1 month')
                        AND orders.status = 'Collected'
                       """)
        row = cursor.fetchone()
        
        total_monthy_cost = row["cost"]
        
    except Exception as e:
        print(str(e))
        print("error will getting the production_cost data")
        raise Exception("error accessing database")
    
    finally:
        cursor.close()
        conn.close()
        
        return total_monthy_cost
        
def get_total_expenses():
    # estblishing a connection to db
    conn = get_db()
    cursor = conn.cursor()
    sum = 0
    data = {}
    
    # get sum of all the expenses in the dictionary 
    try:
        # run SQL query to get data from expenses table
        cursor.execute("""
                       SELECT *
                       FROM expenses
                       """)
        rows = cursor.fetchall()
        
        data = {
            "total_expenses": None,
            "expenses": {}
        }
        
        # iternating over each row in rows and calculating the sum
        for row in rows:
            sum = sum + row["expense_cost"]
            data["expenses"][row["expense"]] = row["expense_cost"]
        
        # adding the sum to the dictionary
        data["total_expenses"] = sum  
        
    except Exception as e:
        print("ERROR: ", str(e))
        print("error accessing the database to get expenses")
        
    finally:
        cursor.close()
        conn.close()
        
        return data
        
def remove_expense(name):
    # establish connection with the db
    conn = get_db()
    cursor = conn.cursor()
    
    # execute sql statmenent
    try:
        cursor.execute("""
                    DELETE FROM expenses
                    WHERE expense = ?
                    """,(name,))
        
        conn.commit()
        
    except Exception as e:
        conn.rollback()
        print("there was an error deleting an expense from the db")
        raise Exception("there was an error accessing the db")
    
    finally:
        cursor.close()
        conn.close()
        
def add_expense(name, amount):
    # establish connection with the db
    conn = get_db()
    cursor = conn.cursor()
    
    # execute sql statmenet
    try:
        cursor.execute("""
                    INSERT INTO expenses
                    (expense, expense_cost)
                    VALUES (?, ?)
                    """, (name, amount,))
        
        conn.commit()
        
    except Exception as e:
        conn.rollback()
        print("there was an error adding an expense to the db")
        raise Exception("there was an error accessing the db")
    
    finally:
        cursor.close()
        conn.close()
        
# function to check if there are any expenses in the table to tell the frontend that there are no more expenses
def check_expenses():
    # establish connection with the db
    conn = get_db()
    cursor = conn.cursor()
    
    # execute sql statmenet
    try:
        cursor.execute("""
                    SELECT *
                    FROM expenses
                    """)
        rows = cursor.fetchall()
        
    except Exception as e:
        conn.rollback()
        print("there was an error accessing the db")
        raise Exception("there was an error accessing the db")
    
    finally:
        cursor.close()
        conn.close()
        
        return 'true' if len(rows) > 0 else 'false'
    
# functions to help with the order Statisitcs pages
def get_number_orders():
    # establish connection with the db
    conn = get_db()
    cursor = conn.cursor()
    
    # execute sql statmenet
    try:
        cursor.execute("""
                    SELECT COUNT(*) AS total_rows
                    FROM orders
                    WHERE order_time >= datetime('now', '-1 month')
                    """)
        row = cursor.fetchone()
        
        total_rows = row["total_rows"]
        
        return total_rows
              
    except Exception as e:
        
        conn.rollback()
        print("there was an error accessing the db")
        raise Exception("there was an error getting order statistics")
    
    finally:
        cursor.close()
        
        
# now getting function to get the number of orders collected
def get_number_orders_collected():
    # establish connection with the db
    
    conn = get_db()
    cursor = conn.cursor()
    
    # execute sql statmenet
    try:
        cursor.execute("""
                    SELECT COUNT(*) AS total_rows
                    FROM orders
                    WHERE status = 'Collected'
                    AND order_time >= datetime('now', '-1 month')
                    """)
        row = cursor.fetchone()
        
        total_rows = row["total_rows"]
        
        return total_rows
              
    except Exception as e:
        
        conn.rollback()
        print("there was an error accessing the db")
        raise Exception("there was an error getting the number of total collected orders")
    
    finally:
        cursor.close()
        conn.close()
        
# function to get the number of orders not collected
def get_number_orders_not_collected():
    # establish connection with the db
    conn = get_db()
    cursor = conn.cursor()
    
    # execute sql statmenet
    try:
        cursor.execute("""
                    SELECT COUNT(*) AS total_rows
                    FROM orders
                    WHERE status != 'Collected'
                    AND order_time >= datetime('now', '-1 month')
                    """)
        row = cursor.fetchone()
        
        total_rows = row["total_rows"]
        
        return total_rows
              
    except Exception as e:
        
        conn.rollback()
        print("there was an error accessing the db")
        raise Exception("there was an error getting the number of total not collected orders")
    
    finally:
        cursor.close()
        
# function to calculate the average quantity of each order
def get_average_order_quantity():
    # establish connection with the db
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # running db qury
        cursor.execute("""
                       WITH order_items_quantity AS (SELECT SUM(order_items.item_quantity) AS total_quantity
                                                    FROM order_items
                                                    JOIN orders ON order_items.order_id = orders.id
                                                    WHERE orders.status = 'Collected'
                                                    AND orders.order_time >= datetime('now', '-1 month')
                                                    GROUP BY order_id )
                                            
                       SELECT AVG(total_quantity) AS average_quantity FROM order_items_quantity
                       """)
        row = cursor.fetchone()
        
        # accessing the data
        average_quantity = row["average_quantity"]
        
        return average_quantity
    
    except Exception as e:
        conn.rollback()
        print("error accessing the db")
        raise Exception("there was an error accessing thee the average order quantity")
    
    finally: 
        # finally closing the connection
        cursor.close()
        conn.close()
        
# creating function to calcaulte the average value of each order
def get_average_order_value():
    # establish connection with the db
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # running db qury
        cursor.execute("""
                       SELECT AVG(total_price) AS average_value
                       FROM orders
                       WHERE status = 'Collected'
                       AND order_time >= datetime('now', '-1 month')
                       """)
        row = cursor.fetchone()
        
        # accessing the data
        average_value = row["average_value"]
        
        return average_value
    
    except Exception as e:
        conn.rollback()
        print("error accessing the db")
        raise Exception("there was an error accessing thee the average order value")
    
    finally: 
        # finally closing the connection
        cursor.close()
        conn.close()
 
# creating function to find the best selling cakes and foods
def get_best_selling_items(type):
    # establish connection with the db
    conn = get_db()
    cursor = conn.cursor()
    
    # safely try to run the SQL query
    try:
        cursor.execute("""
                       WITH item_quantities AS (
                        SELECT items.name, SUM(order_items.item_quantity) AS sum
                        FROM order_items
                        JOIN items
                        ON order_items.item_id = items.id
                        JOIN orders
                        ON order_items.order_id = orders.id  
                        WHERE orders.status = 'Collected'
                            AND items.category = ?
                            AND orders.order_time >= datetime('now', '-1 month')
                        GROUP BY items.name 
                    )


                    SELECT name FROM (
                        SELECT name FROM item_quantities ORDER BY sum DESC LIMIT 1
                    )

                    UNION ALL

                    SELECT name FROM (
                        SELECT name FROM item_quantities ORDER BY sum ASC LIMIT 1
                    );
                """, (type, ))       
        rows = cursor.fetchall()
        
        # now sending the best selling and worst sellinf data back to the caller
        return {
            'best_selling': rows[0]['name'],
            'worst_selling': rows[1]['name']
        }
        
    except Exception as e:
        conn.rollback()
        print("error accessing db")
        raise Exception("there was an error getting back the best ans wrost selling data")
    
    finally:
        cursor.close()
        conn.close()
        
# function to get function to get item data from name and type
def get_item_data_by_name(name, type):
    # establish connection with teh db
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # execute sql
        cursor.execute("""
                    SELECT * FROM items
                    WHERE name = ?
                    AND category = ?
                    """, (name, type, ))
        row = cursor.fetchone()
        
        return row
    
    except Exception as e:
        conn.rollback()
        print("error accessing db")
        raise Exception("error get the best item for thr home page")
    
    finally:
        cursor.close()
        conn.close()
        
# function to write new order to the page
def add_new_item(data):
    # establish connection with the db
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # execute sql
        cursor.execute("""
                        INSERT INTO items
                        (name, price, description, imgsource, category, quantity, production_cost)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        data['name'],
                        data['price'],
                        data['description'],
                        data['imgsource'],
                        data['category'],
                        data['quantity'],
                        data['production_cost']
                    ))
        
        conn.commit()
        
    except Exception as e:
        conn.rollback()
        print("error accessing db")
        raise Exception("there was an error adding the new item")
    
    finally:
        cursor.close()
        conn.close()
        
# creating function to check if the img source already exists in the db
def check_img_source(imgsource):
    # establish connection with the db
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # execute sql
        cursor.execute("""
                    SELECT * FROM items
                    WHERE imgsource = ?
                    """, (imgsource, ))
        row = cursor.fetchone()
        
        return True if row else False
    
    except Exception as e:
        conn.rollback()
        print("error accessing db")
        raise Exception("there was an error checking the img source")
    
    finally:
        cursor.close()
        conn.close()
        
# creating function to check if the name already exists in the db
def check_name(name):
    # establish connection with the db
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # execute sql
        cursor.execute("""
                    SELECT * FROM people
                    WHERE name = ?
                    """, (name, ))
        row = cursor.fetchone()
        
        return True if row else False
    
    except Exception as e:
        conn.rollback()
        print("error accessing db")
        raise Exception("there was an error checking the name")
    
    finally:
        cursor.close()
        conn.close()
        
# creating functin to get the user id for user name
def get_user_id_by_name(name):
    # establish connection with the db
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # execute sql
        cursor.execute("""
                    SELECT id FROM people
                    WHERE name = ?
                    """, (name, ))
        row = cursor.fetchone()
        
        return row['id']
    
    except Exception as e:
        conn.rollback()
        print("error accessing db")
        raise Exception("there was an error getting the user id")
    
    finally:
        cursor.close()
        conn.close()
    