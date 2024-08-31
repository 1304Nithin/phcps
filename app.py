from flask import Flask, render_template, request, jsonify
import csv
import os
import requests

app = Flask(__name__)

USERS_CSV = 'users.csv'

OUTFITS_CSV = 'outfits.csv'


PRODUCTS_CSV = 'products.csv'

def reset_conversation_state():
    return {
        "awaiting_user_existence": True,
        "awaiting_user_id": False,
        "awaiting_name": False,
        "awaiting_password": False,
        "awaiting_topwear_size": False,
        "awaiting_bottomwear_size": False,
        "awaiting_age": False,
        "awaiting_keyword": False,
        "awaiting_satisfaction": False,
        "awaiting_satisfied_product_title": False,
        "awaiting_satisfied_product_url": False,
        "user_id": None,
        "user_name": None,
        "rawKeyword": None,
        "satisfied_product_title": None,
        "satisfied_product_url": None
    }
def simple_chatbot(user_input):
    global conversation_state

    if conversation_state["awaiting_user_existence"]:
        if user_input.lower() == 'y':
            conversation_state["awaiting_user_existence"] = False
            conversation_state["awaiting_user_id"] = True
            return "Please enter your user ID."
        elif user_input.lower() == 'n':
            conversation_state["awaiting_user_existence"] = False
            conversation_state["awaiting_name"] = True
            return "Great! What's your name?"
        else:
            return "Are you an existing user (Y/N)?"

    elif conversation_state["awaiting_user_id"]:
        if user_exists(user_input):
            conversation_state["user_id"] = user_input
            conversation_state["awaiting_user_id"] = False
            conversation_state["awaiting_keyword"] = True
           
            username = get_username(user_input)
            return f"Welcome back, {username}! Please enter what you're looking for today."
        else:
            return "User ID not found. Please enter a valid user ID."

    elif conversation_state["awaiting_name"]:
        conversation_state["user_name"] = user_input
        conversation_state["awaiting_name"] = False
        conversation_state["awaiting_password"] = True
        return "Please create a password."

    elif conversation_state["awaiting_password"]:
        conversation_state["awaiting_password"] = False
        conversation_state["awaiting_topwear_size"] = True
        return "Enter your topwear size (e.g., S, M, L, XL, XXL):"

    elif conversation_state["awaiting_topwear_size"]:
        conversation_state["rawKeyword"] = {"topwear_size": user_input}
        conversation_state["awaiting_topwear_size"] = False
        conversation_state["awaiting_bottomwear_size"] = True
        return "Enter your bottomwear size (e.g., S, M, L, XL, XXL):"

    elif conversation_state["awaiting_bottomwear_size"]:
        conversation_state["rawKeyword"]["bottomwear_size"] = user_input
        conversation_state["awaiting_bottomwear_size"] = False
        conversation_state["awaiting_age"] = True
        return "Enter your age:"

    elif conversation_state["awaiting_age"]:
        conversation_state["rawKeyword"]["age"] = user_input
        
        conversation_state["user_id"] = add_user(
            conversation_state["user_name"],
            user_input,  
            conversation_state["rawKeyword"]["topwear_size"],
            conversation_state["rawKeyword"]["bottomwear_size"],
            conversation_state["rawKeyword"]["age"]
        )
        conversation_state["awaiting_age"] = False
        conversation_state["awaiting_keyword"] = True
        return f"Hello, {conversation_state['user_name']}! Your user ID is {conversation_state['user_id']}. What are you looking for today?"

    elif conversation_state["awaiting_keyword"]:
        # Fetch data from the API but do not use it
        search_url = f"http://localhost/DressUp%20With%20AI/search.php?keyword={user_input}"
        try:
            response = requests.get(search_url)
            if response.status_code == 200:
                import datamodel
                # We are fetching and ignoring the API response
                api_data = response.json()
                # Optionally, save products from API to CSV if needed
                # save_products_to_csv(api_data['products'])
                # Notify user that we're working to find the best fit
                message = ("<p style='font-size: 18px; font-weight: bold;'>We are working our best to find you the best fit product. "
                           "If no exact match is available, we will recommend top-ranked products based on product ranking.</p>"
                           "<p style='font-size: 16px;'>Please note: The bot is under development and may not always provide perfect results.</p>")
            else:
                return "Error fetching products from the API."
        except requests.exceptions.RequestException as e:
            return f"Error: {str(e)}"

        # Use the first product from products.csv instead of API data
        first_product = get_first_product_from_csv()
        if first_product:
            conversation_state["awaiting_satisfaction"] = True
            conversation_state["awaiting_keyword"] = False
            conversation_state["product_iter"] = iter(get_products_from_csv())
            return message + render_product(first_product)
        else:
            return "No products available."

    elif conversation_state["awaiting_satisfaction"]:
        if user_input.lower() == 'yes':
            conversation_state["awaiting_satisfaction"] = False
            return "Great! What else are you looking for today?"
        elif user_input.lower() == 'no':
            conversation_state["awaiting_satisfaction"] = False
            next_product = get_next_product_from_csv()
            if next_product:
                return ("<p>Sorry that the previous product did not meet your expectations. "
                        "Here is another product that might be a better fit for you:</p>" +
                        render_product(next_product))
            else:
                return "No more products available. Please let me know if there's anything else I can assist you with."
        else:
            return "Please enter 'Yes' or 'No'."

    elif conversation_state["awaiting_satisfied_product_title"]:
        conversation_state["satisfied_product_title"] = user_input
        conversation_state["awaiting_satisfied_product_title"] = False
        return "Please enter the URL of the satisfied product."

    elif conversation_state["awaiting_satisfied_product_url"]:
        conversation_state["satisfied_product_url"] = user_input
        conversation_state["awaiting_satisfied_product_url"] = False

        append_satisfied_product(
            conversation_state["user_id"],
            conversation_state["satisfied_product_title"],
            conversation_state["satisfied_product_url"]
        )

        return "Product added to closet. What else are you looking for today?"

    else:
        return "Sorry, I don't understand that. Can you please rephrase?"

def get_products_from_csv():
    if os.path.exists(PRODUCTS_CSV):
        with open(PRODUCTS_CSV, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            return list(reader)
    return []

def get_next_product_from_csv():
    if 'product_iter' in conversation_state:
        try:
            return next(conversation_state["product_iter"])
        except StopIteration:
            return None
    return None

def render_product(product):
    if 'title' in product and 'price' in product and 'product_url' in product:
        title = product['title']
        price = product['price']
        image_url = product.get('image_url', 'placeholder.png')
        product_url = product['product_url']
        
        html = f"<div class='product'>"
        html += f"<h2>{title}</h2>"
        html += f"<p class='price'>Price: {price}</p>"
        html += f"<img src='{image_url}' alt='{title}' class='product-image'>"
        html += f"<a href='{product_url}' target='_blank' class='buy-now'>Buy Now</a>"
        html += f"</div>"
        html += "<p>If not Satisfied try modifying you Request</p>"
        return html
    else:
        print("Incomplete product data:", product)
        return "<p>Product information incomplete.</p>"

def get_first_product_from_csv():
    if os.path.exists(PRODUCTS_CSV):
        with open(PRODUCTS_CSV, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            first_row = next(reader, None)
            return first_row
    return None

def get_username(user_id):
    with open(USERS_CSV, mode='r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['user_id'] == user_id:
                return row['user_name']
    return "User"  

def user_exists(user_id):
    with open(USERS_CSV, mode='r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['user_id'] == user_id:
                return True
    return False


def add_user(user_name, password, topwear_size, bottomwear_size, age):
   
    user_id = 1
    if os.path.exists(USERS_CSV):
        with open(USERS_CSV, mode='r') as f:
            reader = csv.reader(f)
            next(reader, None)  
            for row in reader:
                user_id = int(row[0]) + 1

    
    with open(USERS_CSV, mode='a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([user_id, user_name, password, topwear_size, bottomwear_size, age])

    return user_id


def append_satisfied_product(user_id, product_title, product_url):
    with open(OUTFITS_CSV, mode='a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([user_id, product_title, product_url])


def save_products_to_csv(products):
   
    file_exists = os.path.exists(PRODUCTS_CSV)

    with open(PRODUCTS_CSV, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['title', 'price', 'image_url', 'product_url', 'reviews', 'number_of_reviews', 'rating', 'feedback_count', 'feedback_rating'])

        for product in products:
            writer.writerow([
                product.get('title', ''),
                product.get('price', ''),
                product.get('image_url', ''),
                product.get('product_url', ''),
                product.get('reviews', ''),
                product.get('number_of_reviews', ''),
                product.get('rating', ''),
                product.get('Offers.FeedbackCount', ''),  
                product.get('Offers.FeedbackRating', '')  
            ])


def render_product(product):
  
    if 'title' in product and 'price' in product and 'product_url' in product:
        title = product['title']
        price = product['price']
        image_url = product.get('image_url', 'placeholder.png')
        product_url = product['product_url']
        
        
        html = f"<div class='product'>"
        html += f"<h2>{title}</h2>"
        html += f"<p class='price'>Price: {price}</p>"
        html += f"<img src='{image_url}' alt='{title}' class='product-image'>"
        html += f"<a href='{product_url}' target='_blank' class='buy-now'>Buy Now</a>"
        html += f"</div>"
        html += "<p>If not Satisfied try modifying you Request</p>"
        conversation_state["awaiting_satisfaction"] = True
        return html
    else:
        
        print("Incomplete product data:", product)
        return "<p>Product information incomplete.</p>"

@app.route('/')
@app.route("/index")
def index():
    global conversation_state
    conversation_state = reset_conversation_state() 
    return render_template('index.html')

@app.route('/get_response', methods=['POST'])
def get_response():
    global conversation_state
    user_input = request.form['user_input']
    bot_response = simple_chatbot(user_input.lower())
    return jsonify({'response': bot_response})

if __name__ == '__main__':
    app.run(debug=True, port=4949)
