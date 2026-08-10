import sqlite3
from flask import Flask, render_template, request, redirect
import math

app = Flask(__name__)

def create_database():

    conn = sqlite3.connect("food_demand.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS restaurants(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        restaurant_name TEXT,
        location TEXT,
        rating REAL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS delivery_agents(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_name TEXT,
    phone TEXT,
    area TEXT
    )
   """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS food_orders(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_name TEXT,
    restaurant_name TEXT,
    food_item TEXT,
    quantity INTEGER,
    price REAL,
    order_status TEXT
)
""")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
)
""")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS prediction_history(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    restaurant_name TEXT,
    food_item TEXT,
    quantity INTEGER,
    prediction TEXT
)
""")

    conn.commit()
    conn.close()

@app.route("/")
def home():
    return redirect("/login")

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("food_demand.db")
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, password)
        )

        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("food_demand.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        )

        user = cursor.fetchone()

        conn.close()

        if user:
            return redirect("/dashboard")
        else:
            return "Invalid Username or Password"

    return render_template("login.html")

@app.route("/dashboard")
def dashboard():

    conn = sqlite3.connect("food_demand.db")
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM restaurants")
    restaurants = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM delivery_agents")
    agents = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM food_orders")
    orders = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(price) FROM food_orders")
    total_revenue = cursor.fetchone()[0]

    if total_revenue is None:
     total_revenue = 0

    cursor.execute("""
    SELECT COUNT(*)
    FROM food_orders
    WHERE LOWER(TRIM(order_status)) = 'pending'
    """)
    pending = cursor.fetchone()[0]

    cursor.execute("""
    SELECT COUNT(*)
    FROM food_orders
    WHERE LOWER(TRIM(order_status)) = 'delivered'
    """)
    delivered = cursor.fetchone()[0]

    cursor.execute("""
    SELECT IFNULL(SUM(price),0)
    FROM food_orders
    WHERE LOWER(order_status)='delivered'
    """)
    revenue = cursor.fetchone()[0]

    
    cursor.execute("""
    SELECT id, customer_name, restaurant_name, food_item, order_status
    FROM food_orders
    ORDER BY id DESC
    LIMIT 5
    """)

    recent_orders = cursor.fetchall()

    conn.close()

    print(restaurants, agents, orders, pending, delivered)

    return render_template(
        "dashboard.html",
        restaurants=restaurants,
        agents=agents,
        orders=orders,
        pending=pending,
        delivered=delivered,
        revenue=revenue,
        recent_orders=recent_orders
    )

@app.route("/view_restaurants")
def view_restaurants():

    conn = sqlite3.connect("food_demand.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM restaurants")

    restaurants = cursor.fetchall()

    conn.close()

    return render_template("view_restaurants.html", restaurants=restaurants)

@app.route("/edit_restaurant/<int:restaurant_id>")
def edit_restaurant(restaurant_id):

    conn = sqlite3.connect("food_demand.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM restaurants WHERE id=?",
        (restaurant_id,)
    )

    restaurant = cursor.fetchone()

    conn.close()

    return render_template(
        "edit_restaurant.html",
        restaurant=restaurant
    )


@app.route("/update_restaurant", methods=["POST"])
def update_restaurant():

    restaurant_id = request.form["restaurant_id"]
    restaurant_name = request.form["restaurant_name"]
    location = request.form["location"]
    rating = request.form["rating"]

    conn = sqlite3.connect("food_demand.db")
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE restaurants
    SET restaurant_name=?,
        location=?,
        rating=?
    WHERE id=?
    """, (
        restaurant_name,
        location,
        rating,
        restaurant_id
    ))

    conn.commit()
    conn.close()

    return redirect("/view_restaurants")

@app.route("/delete_restaurant/<int:restaurant_id>")
def delete_restaurant(restaurant_id):

    conn = sqlite3.connect("food_demand.db")
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM restaurants WHERE id=?",
        (restaurant_id,)
    )

    conn.commit()
    conn.close()

    return redirect("/view_restaurants")

@app.route("/add_restaurant", methods=["GET", "POST"])
def add_restaurant():

    if request.method == "POST":
        restaurant_id = request.form["restaurant_id"]
        restaurant_name = request.form["restaurant_name"]
        location = request.form["location"]
        rating = request.form["rating"]

        conn = sqlite3.connect("food_demand.db")
        cursor = conn.cursor()

        cursor.execute(
    """
    INSERT INTO restaurants
    (id, restaurant_name, location, rating)
    VALUES (?, ?, ?, ?)
    """,
    (
        restaurant_id,
        restaurant_name,
        location,
        rating
    )
)

        conn.commit()
        conn.close()

        return redirect("/dashboard")

    return render_template("add_restaurant.html")

@app.route("/add_delivery_agent", methods=["GET", "POST"])
def add_delivery_agent():

    if request.method == "POST":
        agent_id = request.form["agent_id"]
        agent_name = request.form["agent_name"]
        phone = request.form["phone"]
        area = request.form["area"]

        conn = sqlite3.connect("food_demand.db")
        cursor = conn.cursor()

        cursor.execute("""
INSERT INTO delivery_agents
(id, agent_name, phone, area)
VALUES (?, ?, ?, ?)
""", (
    agent_id,
    agent_name,
    phone,
    area
))
        conn.commit()
        conn.close()

        return redirect("/dashboard")

    return render_template("add_delivery_agent.html")

@app.route("/view_delivery_agents")
def view_delivery_agents():

    conn = sqlite3.connect("food_demand.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM delivery_agents")

    agents = cursor.fetchall()

    conn.close()

    return render_template("view_delivery_agents.html", agents=agents)

@app.route("/edit_delivery_agent/<int:agent_id>")
def edit_delivery_agent(agent_id):

    conn = sqlite3.connect("food_demand.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM delivery_agents WHERE id=?",
        (agent_id,)
    )

    agent = cursor.fetchone()

    conn.close()

    return render_template(
        "edit_delivery_agent.html",
        agent=agent
    )

@app.route("/update_delivery_agent", methods=["POST"])
def update_delivery_agent():

    agent_id = request.form["agent_id"]
    agent_name = request.form["agent_name"]
    phone = request.form["phone"]
    area = request.form["area"]

    conn = sqlite3.connect("food_demand.db")
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE delivery_agents
    SET agent_name=?,
        phone=?,
        area=?
    WHERE id=?
    """, (
        agent_name,
        phone,
        area,
        agent_id
    ))

    conn.commit()
    conn.close()

    return redirect("/view_delivery_agents")

@app.route("/delete_delivery_agent/<int:agent_id>")
def delete_delivery_agent(agent_id):

    conn = sqlite3.connect("food_demand.db")
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM delivery_agents WHERE id=?",
        (agent_id,)
    )

    conn.commit()
    conn.close()

    return redirect("/view_delivery_agents")

@app.route("/add_food_order", methods=["GET", "POST"])
def add_food_order():


    if request.method == "POST":
        customer_name = request.form["customer_name"]
        restaurant_name = request.form["restaurant_name"]
        food_item = request.form["food_item"]
        quantity = request.form["quantity"]
        price = request.form["price"]
        order_status = request.form["order_status"]

        conn = sqlite3.connect("food_demand.db")
        cursor = conn.cursor()

        cursor.execute("""
INSERT INTO food_orders
( customer_name, restaurant_name, food_item, quantity, price, order_status)
VALUES (?, ?, ?, ?, ?, ?)
""", (

    customer_name,
    restaurant_name,
    food_item,
    quantity,
    price,
    order_status
))

        conn.commit()
        conn.close()

        return redirect("/dashboard")

    return render_template("add_food_order.html")

@app.route("/view_food_orders")
def view_food_orders(): 

    conn = sqlite3.connect("food_demand.db")
    cursor = conn.cursor()

    page = request.args.get("page", 1, type=int)
    per_page = 5

    search = request.args.get("search", "").strip()
    status = request.args.get("status", "").strip()
    sort = request.args.get("sort", "").strip()

    query = "SELECT * FROM food_orders WHERE 1=1"
    values = []

    if search != "":
        query += " AND customer_name LIKE ?"
        values.append("%" + search + "%")

    if status != "":
        query += " AND LOWER(order_status)=?"
        values.append(status.lower())

    if sort == "newest":
        query += " ORDER BY id DESC"

    elif sort == "oldest":
        query += " ORDER BY id ASC"

    elif sort == "price_low":
        query += " ORDER BY price ASC"

    elif sort == "price_high":
        query += " ORDER BY price DESC"

    offset = (page - 1) * per_page

    query += " LIMIT ? OFFSET ?"
    values.extend([per_page, offset])

    cursor.execute(query, values)
    orders = cursor.fetchall()

    count_query = "SELECT COUNT(*) FROM food_orders WHERE 1=1"
    count_values = []

    if search != "":
        count_query += " AND customer_name LIKE ?"
        count_values.append("%" + search + "%")

    if status != "":
        count_query += " AND LOWER(order_status)=?"
        count_values.append(status.lower())

    cursor.execute(count_query, count_values)
    total_orders = cursor.fetchone()[0]

    total_pages = math.ceil(total_orders / per_page)

    print("ORDERS =", orders)

    conn.close()

    return render_template(
        "view_food_orders.html",
        orders=orders,
        page=page,
        total_pages=total_pages
    )

@app.route("/edit_food_order/<int:order_id>")
def edit_food_order(order_id):

    conn = sqlite3.connect("food_demand.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM food_orders WHERE id=?",
        (order_id,)
    )

    order = cursor.fetchone()

    conn.close()

    return render_template(
        "edit_food_order.html",
        order=order
    )

@app.route("/save_food_order", methods=["POST"])
def update_food_order():

    order_id = request.form["order_id"]
    customer_name = request.form["customer_name"]
    restaurant_name = request.form["restaurant_name"]
    food_item = request.form["food_item"]
    quantity = request.form["quantity"]
    price = request.form["price"]
    order_status = request.form["order_status"]

    conn = sqlite3.connect("food_demand.db")
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE food_orders
    SET customer_name=?,
        restaurant_name=?,
        food_item=?,
        quantity=?,
        price=?,
        order_status=?
    WHERE id=?
    """, (
        customer_name,
        restaurant_name,
        food_item,
        quantity,
        price,
        order_status,
        order_id
    ))

    conn.commit()
    conn.close()

    return redirect("/view_food_orders")

@app.route("/delete_food_order/<int:order_id>")
def delete_food_order(order_id):

    conn = sqlite3.connect("food_demand.db")
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM food_orders WHERE id=?",
        (order_id,)
    )

    conn.commit()
    conn.close()

    return redirect("/view_food_orders")

@app.route("/prediction", methods=["GET", "POST"])
def prediction():

    result = ""

    if request.method == "POST":

        restaurant = request.form["restaurant_name"]
        food_item = request.form["food_item"]
        quantity = int(request.form["quantity"])

        if quantity >= 10:
            result = "High Demand"
        else:
            result = "Low Demand"

        conn = sqlite3.connect("food_demand.db")
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO prediction_history
        (restaurant_name, food_item, quantity, prediction)
        VALUES (?, ?, ?, ?)
        """, (
        restaurant,
        food_item,
        quantity,
        result
        ))

        conn.commit()
        conn.close()

        return render_template(
            "prediction.html",
            result=result
        )

    return render_template("prediction.html")

@app.route("/prediction_history")
def prediction_history():

    conn = sqlite3.connect("food_demand.db")
    cursor = conn.cursor()

    search = request.args.get("search", "").strip()

    page = request.args.get("page", 1, type=int)
    per_page = 5

    query = "SELECT * FROM prediction_history WHERE 1=1"
    values = []


    if search != "":
        query += " AND restaurant_name LIKE ?"
        values.append("%" + search + "%")

    query += " ORDER BY id DESC"

    offset = (page - 1) * per_page

    query += " LIMIT ? OFFSET ?"
    values.extend([per_page, offset])

    cursor.execute(query, values)
    predictions = cursor.fetchall()
    cursor.execute("SELECT COUNT(*) FROM prediction_history")
    total_predictions = cursor.fetchone()[0]

    total_pages = math.ceil(total_predictions / per_page)
    conn.close()

    return render_template(
        "prediction_history.html",
        predictions=predictions,
        page=page,
        total_pages=total_pages
    )
@app.route("/edit_prediction/<int:prediction_id>")
def edit_prediction(prediction_id):

    conn = sqlite3.connect("food_demand.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM prediction_history WHERE id=?",
        (prediction_id,)
    )

    prediction = cursor.fetchone()

    conn.close()

    return render_template(
        "edit_prediction.html",
        prediction=prediction
    )

@app.route("/update_prediction", methods=["POST"])
def update_prediction():

    prediction_id = request.form["prediction_id"]
    restaurant_name = request.form["restaurant_name"]
    food_item = request.form["food_item"]
    quantity = int(request.form["quantity"])

    if quantity >= 10:
        prediction = "High Demand"
    else:
        prediction = "Low Demand"

    conn = sqlite3.connect("food_demand.db")
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE prediction_history
    SET restaurant_name=?,
        food_item=?,
        quantity=?,
        prediction=?
    WHERE id=?
    """, (
        restaurant_name,
        food_item,
        quantity,
        prediction,
        prediction_id
    ))

    conn.commit()
    conn.close()

    return redirect("/prediction_history")


@app.route("/delete_prediction/<int:prediction_id>")
def delete_prediction(prediction_id):

    conn = sqlite3.connect("food_demand.db")
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM prediction_history WHERE id=?",
        (prediction_id,)
    )

    conn.commit()
    conn.close()

    return redirect("/prediction_history")

@app.route("/logout")
def logout():
    return redirect("/login")   

if __name__ == "__main__":
    create_database()
    app.run(debug=True)