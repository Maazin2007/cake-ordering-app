from flask import Flask, render_template, request, json, session, flash, redirect
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
from auth_helpers import checkmail, check_mail_exists, add_new_user, user_id_by_mail, check_password, login_required, check_admin, get_items
from flask import session, redirect, jsonify, url_for
from sql_helpers import check_item, get_cart, get_item_price, place_order, get_orders, update_order, get_orders_admin, get_total_revenue, get_total_cost, get_total_expenses, remove_expense, add_expense, check_expenses, get_number_orders, get_number_orders_collected, get_number_orders_not_collected, get_average_order_quantity, get_average_order_value, get_best_selling_items, get_item_data_by_name, add_new_item, check_img_source, check_name, get_user_id_by_name
import sqlite3
from functools import wraps
import os
from werkzeug.utils import secure_filename

# creating application
app = Flask(__name__)

# ensuring that I can make like changes to flask
app.debug = True

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configuration
UPLOAD_FOLDER = 'static/images'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Helper to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# home page route
@app.route("/")
def index():
    
    # this is just for the top
    status = "chicken"
    status_admin = "chicken"
    
    if "user_id" in session:
        status = 'login'
        if check_admin(session["user_id"]):
            status_admin = 'admin'
            
    # this to get the best selling items from the cakes and food table
    cake_data = get_best_selling_items('cake')
    best_selling_cake = cake_data['best_selling']
    
    food_data = get_best_selling_items('food')
    best_selling_food = food_data['best_selling']
    
    # now we need to get the whole data for each of the cake and food
    cake_data = get_item_data_by_name(best_selling_cake, 'cake')
    food_data = get_item_data_by_name(best_selling_food, 'food')
    
     
    return render_template("index.html", status=status, status_admin=status_admin, cake_data=cake_data, food_data=food_data)

#login page route
@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        user_mail = request.form.get("mail")
        user_password = request.form.get("password")
        
        check_list = [user_mail, user_password]
        
        for element in check_list:
            if element == "":
                flash("Invalid Submission", "errorDisplay")
                return redirect("/login")
        
        if not check_mail_exists(user_mail):
            flash("Mail does not exist", "error_mail")
            return redirect("/login")
        
        if  check_password(user_mail, user_password):
            session["user_id"] = user_id_by_mail(user_mail)
            return redirect("/")
        else:
            flash("incorrect password", "error_password")
            return redirect("/login")
        
    else: 
        return render_template("login.html")
    
# registration page route
@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        # getting all the data from the form and storing it in variables
        user_email = request.form.get("mail")
        user_name = request.form.get("name")
        user_password = request.form.get("password")
        user_password_confirm = request.form.get("password_confirm")
        
        # checking if any of the variables are empty
        checking_list = [user_email, user_name, user_password, user_password_confirm]
        
        # iterating over the list to find any empty strings
        for detail in checking_list:
            if detail == "":
                flash("incorrect form submission", "errorDisplay")
                return redirect("/register")
            
        # check if the email entered is valid
        if not checkmail(user_email):
            flash("Error: invalid mail", "mail_error")
            return redirect("/register")
        
        # check if the mail is already registered
        if check_mail_exists(user_email):
            flash("You are already registered! Please Log in", "loginDisplay")
            return redirect("/login")
        
        # putting the mail to lower and removing and whitespaces
        user_email = user_email.lower().strip()
        
        # checking if both passwords match
        if not user_password == user_password_confirm:
            flash("passwords do not match", "password_error")
            return redirect("/register")
        
        # generating password hash
        password_hash = generate_password_hash(user_password)
        
        # store the new user in the database
        add_new_user(user_name, user_email, password_hash)
        
        # adding user to session and then routing to homepage
        session["user_id"] = user_id_by_mail(user_email)
        
        return redirect("/")
        
    else:
        return render_template("register.html")
    
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/cakes")
def cakespage():
    # fetching all the cake data and sending it to the template
    items = get_items()
    
    status = "chicken"
    status_admin = "chicken"
    
    if "user_id" in session:
        status = 'login'
        if check_admin(session["user_id"]):
            status_admin = 'admin'
    
    return render_template("cakes.html", items=items, status=status, status_admin=status_admin)

@app.route("/admin")
def admin():
    # code for the login and logout button on top and the admin check 
    status = "chicken"
    status_admin = "chicken"
    
    if "user_id" in session:
        status = 'login'
        if check_admin(session["user_id"]):
            status_admin = 'admin'
            
    # getting the orders history from the sql table
    try:
        orders = get_orders_admin()
    except Exception as e:
        print("there was an error: ", str(e))
        orders = {}
        
    # now we have to get the finance section data
    revenue = None
    cost = None
    expenses = None
    
    # STEP 1: first get the total revenue of the past month and the total production cost
    try:
        revenue = get_total_revenue()
        cost = get_total_cost()
        expenses = get_total_expenses()
        
    except Exception as e:
        print("there was an error", str(e))
    
    # STEP 2: Calculate the profit
    profit = revenue - (cost + expenses["total_expenses"])
    profit_status = "true"
    
    percentageProfit = 0
    costPercentage = 0
    expensesPercentage = 0
    percentageLoss = 0
    
    if profit < 0:
        profit_status = "false"
        profit = profit * -1
        percentageLoss = round((1 * profit) / revenue * 100, 2)

    else:
        percentageProfit = round(profit / revenue * 100, 2)
        costPercentage = cost / revenue * 100
        expensesPercentage = 100 - (percentageProfit + costPercentage)
            
    
    # STEP 3: compile data in a dictionary and send to the front-end as a parameter
    data = {
        "revenue": revenue,
        "cost": cost,
        "profit": profit,
        "percentageProfit": percentageProfit,
        "costPercentage": costPercentage,
        "expensesPercentage": expensesPercentage,
        "profit_status": profit_status, 
        "percentageLoss": percentageLoss
    }
    
    # Getting the order statistics
    try:
        total_number_orders = get_number_orders()
        total_collected_orders = get_number_orders_collected()
        total_pending_orders = get_number_orders_not_collected()
        average_order_quantity = round(get_average_order_quantity())
        average_order_value  = get_average_order_value()
        cake_data = get_best_selling_items('cake')
        food_data = get_best_selling_items('food')
        
    except Exception as e:
        print("there was an error: ", str(e))
        
    # adding the data to the data object to send to the front-end
    data["total_number_orders"] = total_number_orders
    data["total_collected_orders"] = total_collected_orders
    data["total_pending_orders"] = total_pending_orders
    data["average_order_quantity"] = average_order_quantity
    data["average_order_value"] = average_order_value
    data["cake_data"] = cake_data
    data["food_data"] = food_data
        
    # STEP 4: render template
    return render_template("admin.html", status=status, status_admin=status_admin, orders=orders, data=data, expenses=expenses)

@app.route("/foods")
def foods():
    items = get_items()
    
    status = "chicken"
    status_admin = "chicken"
    
    if "user_id" in session:
        status = 'login'
        if check_admin(session["user_id"]):
            status_admin = 'admin'
    
    return render_template("food.html", items=items, status=status, status_admin=status_admin)

@app.route("/cart", methods=["GET", "POST"])
@login_required
def cart():
    status = "chicken"
    status_admin = "chicken"
    
    if "user_id" in session:
        status = 'login'
        if check_admin(session["user_id"]):
            status_admin = 'admin'
            
    if request.method == "POST":
        item_id = request.form.get("item_id")
        
        # if no input is send send back to the homepage
        if not item_id: return redirect(request.referrer or "/")
    
        # coverting the id to int 
        try:
            item_id = int(item_id)
        except ValueError:
            return redirect(request.referrer or "/")
        
        # if cart does not exist in session set it to empty list
        if "cart" not in session:
            session["cart"] = {}
            
        # checking if the ID of the item coming to the server exists
        if not check_item(item_id): return redirect(request.referrer or "/")
        
        if str(item_id) not in session["cart"]:
            session["cart"][str(item_id)] = {"amount": 1}  # create key and assign quantity 1
        else:
            session["cart"][str(item_id)]["amount"] += 1  # increment quantity if exists

        # return to the page which the request came from 
        return redirect("/cart")
        
    else:
        sum_cal = 0
        tax = 0
        total = 0
        calculation = []
        
        if "cart" not in session or not session["cart"]:
            cart = "empty"
        else:
            enriched_cart = get_cart(session["cart"].copy())
            
            # getting the price of each element and storing inside a list
            for key in enriched_cart:
                calculation.append(get_item_price(key) * enriched_cart[key]["amount"])
                
            sum_cal = sum(calculation)
            tax = round(0.15 * sum_cal, 1)
            total = sum_cal + tax
            
            cart = enriched_cart
            
        return render_template("cart.html", cart = cart, status=status, status_admin=status_admin, sum=sum_cal, tax=tax, total=total)
    
@app.route("/removeCartItem", methods=["POST"])
def removeCartItem():
    if request.method == "POST":
        # getting the item id
        item_id = request.form.get("item_id")
        
        # trying to convert item_id to integer
        try:
            item_id = int(item_id)
        except ValueError:
            return redirect("/cart")
        
        # checking if the item_id recieved is inside the cart
        if str(item_id) not in session["cart"]:
            return redirect("/cart")
        
        # removing the item id from the cart list 
        del session["cart"][str(item_id)]
            
        # return back to the cart page 
        return redirect("/cart")
    
    
@app.route("/get-cart")
def getCart():
    try:
        raw_cart = session.get("cart", {})
        enriched_cart = get_cart(raw_cart.copy())
        
        return jsonify(enriched_cart), 200
    
    except Exception as e:
        return jsonify({"error": "failed to load"}), 500

@app.route("/update-cart", methods=["POST"])
def updateCart():
    try:
        data = request.get_json()
        session["cart"] = data
        
        return jsonify({"message": "successfully updated"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}, 500)
    
@app.route("/place-order", methods=["POST"])
@login_required
def placeOrder():
    # first we need to store session cart in a variable for ease
    cart = session["cart"]
    user_id = session["user_id"]
    
    # send cart to helper function to store in database
    place_order(cart, user_id)
    
    session["cart"] = {}
    # redirect to the orders page
    return redirect("/orders")
    
@app.route("/orders", methods=["GET"])
@login_required
def orders():
    status = "chicken"
    status_admin = "chicken"
    
    if "user_id" in session:
        status = 'login'
        if check_admin(session["user_id"]):
            status_admin = 'admin'

    # get a list of orders there status and a number of things 
    orders_dict = get_orders(session["user_id"])
    
    print(orders_dict)
    
    # render the orders page
    return render_template("orders.html", orders=orders_dict, status=status, status_admin=status_admin)
    
@app.route("/update-order", methods=["POST"])
def update():
    # Step 1: check if the incoming object is a JSON
    if not request.is_json:
        # return error and end function
        return jsonify({"error": "inccorect object format", "details" : "object is not JSON format"}), 400
    
    # Step 2: safely parse the JSON object
    try:
        data = request.get_json() 
    except Exception as e:
        # return error and end function
        return jsonify({"error": "unable to parse object", "details": "cannot parse JSON object to python format"}), 400
    
    # Step 3: check if keys are the same as we orginall designed
    valid_keys = ["user_id", 'order_id', 'status']
    for key in data:
        if key not in valid_keys:
            # return error and end function
            return jsonify({"error": "object error", "details": "object does not have the expected keys"}), 400
        
    # Step 4: extracting values from incoming object
    status = data["status"]
    order_id, user_id = None, None
    
    try:
        order_id = int(data["order_id"])
        user_id = int(data["user_id"])
        
    except ValueError:
        print("error will converting to int while updating order")
        return jsonify({"error": "conversion", "details": "failed to convert string sent to int"}), 400
    
    # Step 5: updating the database and checking the values of the data key
    try:
        if status == "ready":
            update_order("Ready", order_id, user_id)
        elif status == "collected":
            update_order("Collected", order_id, user_id)
        else:
            return jsonify({"error": "error in object", "details": "the value of the key are not collected or ready for pickup"}), 400
        
    except Exception as e:
        return jsonify({"error": "database error", "details" : str(e)}), 500
        
    return jsonify({"success": "cart has been successfully updated"}), 200
    
@app.route("/api/update-expense", methods=["POST"])
def updateExpense():
    # STEP 1: Check if the data coming from the front-end in an json format
    if not request.is_json:
        return jsonify({'error': 'error parsing JSON object', 'details': 'object is not a JSON'}), 400
    
    # STEP 2: safely parse the JSON object to python format
    # declare the variable to store the data
    data = None
    
    # trying to access JSON data safely
    try: 
        data = request.get_json()
        print('data has been successfully retrieved from the JSON object to update the expense')
        
    except Exception as e:
        # print error message to the terminal
        print('system was not able to parse the JSON object')
        # send back error 200 and error dict to the front-end
        return jsonify({'error': 'error parsing JSON object', 'details': 'could not safely access the JSON object data'}), 400
    
    # STEP 3: check if the keys match the keys you want to prevent user manipulation
    
    # checking if the JSON response holds the list
    required_keys = ['expense_name', 'expense_amount', 'action']
    missing_keys = [key for key in required_keys if key not in data]
    
    # checking if there is any keys in the missing keys list
    if missing_keys:
        error_details = f"object is missing keys {missing_keys}"
        return jsonify({'error': 'error parsing JSON object', 'details': error_details}), 400
    
    # STEP 4: now executing actions with the data
    
    # checking the action is delete or add
    if data["action"] == 'delete':
        # remove the expense from the table
        try: 
            remove_expense(data["expense_name"])
        except Exception as e:
            return jsonify({'error': 'error removing expense', 'details': str(e)}), 400
        
    elif data["action"] == 'add':
        # adding expense to the table
        try:
            add_expense(data["expense_name"], data["expense_amount"])
        except Exception as e:
            return jsonify({'error': 'error adding expense', 'details': str(e)}), 400   
    
    else:
        # returning error object if action key does not have the 2 above values
        return jsonify({'error': 'error in object keys', 'details': 'the action key should only have add or remove'}), 400
    
    
    empty_status = check_expenses()
    
    # STEP 4: send back success message
    return jsonify({'success': f'successfull API request', 'details': f'successfully {data["action"]} from expense', 'expense_status': f'{empty_status}'}), 200

@app.route("/api/get-finance-object")
def getFinanceObject():
    
    # getting the orders history from the sql table
    data = None
    
    try:
        data = get_orders_admin()
    except Exception as e:
        print("there was an error: ", str(e))
        return jsonify({"error": "thete an error hadeling the db", 'details': 'access order history in the finance object'}), 400
        
    # now we have to get the finance section data
    revenue = None
    cost = None
    expenses = None
    
    # STEP 1: first get the total revenue of the past month and the total production cost
    try:
        revenue = get_total_revenue()
        cost = get_total_cost()
        expenses = get_total_expenses()
        
    except Exception as e:
        print("there was an error", str(e))
    
    # STEP 2: Calculate the profit
    profit = revenue - (cost + expenses["total_expenses"])
    profit_status = "true"
    
    percentageProfit = 0
    costPercentage = 0
    expensesPercentage = 0
    percentageLoss = 0
    
    if profit < 0:
        profit_status = "false"
        profit = profit * -1
        percentageLoss = round((1 * profit) / revenue * 100, 2)
        
    else:
        percentageProfit = round(profit / revenue * 100, 2)
        costPercentage = round(cost / revenue * 100, 2)
        expensesPercentage = 100 - (percentageProfit + costPercentage)
            
    
    # STEP 3: compile data in a dictionary and send to the front-end as a parameter
    expenses_message = expenses["total_expenses"]
    
    data = {
        "revenue": revenue,
        "cost": cost,
        "profit": profit,
        "percentageProfit": percentageProfit,
        "costPercentage": costPercentage,
        "expensesPercentage": expensesPercentage,
        "profit_status": profit_status, 
        "percentageLoss": percentageLoss,
        "expenses": expenses_message
    }
    
    # STEP 4: compile data in a dictionary and send to the front-end as a parameter
    # send back the object
    print("sending back the object")
    return jsonify(data), 200
    
# coding API endpoint to add item to the db
@app.route('/api/adding-item', methods=['POST'])
def adding_item():
    # Check if image file is in the request
    if 'image' not in request.files:
        return jsonify({'error': 'Image missing', 'details': 'No image file part in request'}), 400
    
    image = request.files['image']
    
    # Check if the image file has a valid filename
    if image.filename == '':
        return jsonify({'error': 'Image missing', 'details': 'No image selected'}), 400
    
    if image and allowed_file(image.filename):
        # Secure the filename
        filename = secure_filename(image.filename)

        # Prevent file overwrite
        full_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(full_path):
            return jsonify({'error': 'Image exists', 'details': 'Image with same name already exists'}), 400

        # Save the file
        image.save(full_path)
    else:
        return jsonify({'error': 'Invalid image type', 'details': 'Only .jpg or .jpeg allowed'}), 400

    # Get other form fields
    try:
        name = request.form['name'].strip()
        price = float(request.form['price'])
        description = request.form['description'].strip()
        category = request.form['category']
        quantity = int(request.form['quantity'])
        production_cost = float(request.form['production_cost'])

        if not name or not description:
            raise ValueError("Name and description cannot be empty.")
        if category not in ['cake', 'food']:
            raise ValueError("Invalid category")
        if price <= 0 or quantity <= 0 or production_cost <= 0:
            raise ValueError("Numerical values must be positive")
    except Exception as e:
        # Optionally delete the saved image if data is invalid
        if os.path.exists(full_path):
            os.remove(full_path)
        return jsonify({'error': 'Invalid form data', 'details': str(e)}), 400

    # Check image name in DB
    if check_img_source(full_path):
        return jsonify({'error': 'Image exists in DB', 'details': 'imgsource already exists in DB'}), 400

    # Save to DB
    try:
        data = {
            'name': name,
            'price': price,
            'description': description,
            'imgsource': full_path,
            'category': category,
            'quantity': quantity,
            'production_cost': production_cost
        }
        add_new_item(data)
    except Exception as e:
        if os.path.exists(full_path):
            os.remove(full_path)
        return jsonify({'error': 'DB error', 'details': 'Could not add item to DB'}), 400

    return jsonify({'success': 'successful API request', 'details': 'Successfully added item to the DB'}), 200

# coding API to send order assoicated with that name to the front-end
@app.route('/api/get-order-by-name', methods = ['POST'])
def get_orders_by_name_api():
    # check if the icoming object is JSON
    if not request.is_json:
        # sending error 40
        return jsonify({'error': 'Invalid Request', 'details': 'object not in JSON format'}), 400
    
    # safely parsing JSON object
    data = None
    
    try:
        data = request.get_json()
    except Exception as e:
        print('Error: ', str(e))
        return jsonify({'error': 'Invalid JSON', 'details': 'error trying to parse JSON object'}), 404
    
    # check if the keys exist
    if 'name' not in data:
        print('name key not in JSON object')
        return jsonify({'error': 'Invalid Request', 'details': 'name key should be in JSON object'}), 400 
    
    # removing leading and trailing spaces
    name = data['name'].strip()
    data['name'] = name
    
    # check if the name exists
    try:
        if not check_name(data['name']):
            print('name does not exist')
            return jsonify({'error': 'Conflict', 'details': 'name does not exist'}), 400
    except Exception as e:
        print('error accessing db')
        return jsonify({'error': 'Database Error', 'details': 'error accessing db to check name'}), 500
    
    # get orders dictionary
    orders = None

    try:
        user_id = get_user_id_by_name(data['name'])
        orders = get_orders(user_id)
        print(orders)
        
    except Exception as e:
        print('error:', str(e))
        return jsonify({'error': 'Database Error', 'details': f'error getting orders for {data['name']}'}), 500
    
    # sending orders to the front-end
    return jsonify({'success': 'successful API request', 'details': 'succesfully got orders', 'orders': orders}), 200