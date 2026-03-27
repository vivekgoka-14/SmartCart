from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime, timedelta
from functools import wraps
from flask_mail import Mail, Message
import random
import string

app = Flask(__name__)
app.secret_key = 'smartcart_secret_key_123'

# Flask-Mail Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'gokavivek@gmail.com'
app.config['MAIL_PASSWORD'] = 'nldhdgdjqxptgpxu'
app.config['MAIL_DEFAULT_SENDER'] = 'gokavivek@gmail.com'
mail = Mail(app)

# MongoDB Configuration
client = MongoClient('mongodb+srv://vivek14:vivek14@cluster0.omh6d9q.mongodb.net/?appName=Cluster0')
db = client['smartcart_db']

users_col = db['users']
products_col = db['products']
orders_col = db['orders']
categories_col = db['categories']
reviews_col = db['reviews']
subscriptions_col = db['subscriptions']
notifications_col = db['notifications']
discounts_col = db['discounts']
product_tracking_col = db['product_tracking']


# Decorators
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'danger')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'admin':
            flash('Admin access required.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# Context Processor for Cart Total
@app.context_processor
def inject_cart():
    cart_count = 0
    cart_total = 0
    if 'cart' in session:
        for item_id, item_data in session['cart'].items():
            cart_count += item_data['qty']
            if item_id.startswith('mock_'):
                cart_total += item_data.get('price', 0) * item_data['qty']
            else:
                product = products_col.find_one({'_id': ObjectId(item_id)})
                if product:
                    cart_total += product.get('price', 0) * item_data['qty']
    return dict(cart_count=cart_count, cart_total=cart_total)

@app.context_processor
def inject_all_products():
    all_products = list(products_col.find({}, {'name': 1, '_id': 1}))
    # Convert ObjectId to string for JSON serialization
    for p in all_products:
        p['_id'] = str(p['_id'])
    return dict(all_products_list=all_products)

# --- PUBLIC PAGES ---

@app.route('/')
def index():
    featured_products = list(products_col.find().limit(8))
    categories = list(categories_col.find())
    fruits = list(products_col.find({'category': 'Fresh Fruits'}).limit(8))
    vegetables = list(products_col.find({'category': 'Vegetables'}).limit(8))
    return render_template('index.html', 
                          products=featured_products, 
                          categories=categories,
                          fruits=fruits,
                          vegetables=vegetables)

@app.route('/chatbot/query', methods=['POST'])
@login_required
def chatbot_query():
    data = request.json
    user_msg = data.get('message', '').lower()
    user_id = session.get('user_id')
    
    response_text = ""
    recommendations = []
    
    # Simple keyword matching for Sahaayi AI
    if 'fruit' in user_msg:
        recommendations = list(products_col.find({'category': 'Fresh Fruits'}).limit(3))
        response_text = "I recommend checking out our fresh fruits! They are just arrived from the farm."
    elif 'veg' in user_msg or 'vegetable' in user_msg:
        recommendations = list(products_col.find({'category': 'Vegetables'}).limit(3))
        response_text = "We have a variety of fresh organic vegetables today. Have a look!"
    elif 'drink' in user_msg or 'beverage' in user_msg or 'juice' in user_msg:
        recommendations = list(products_col.find({'category': {'$in': ['Drinks', 'Beverages']}}).limit(3))
        response_text = "Thirsty? Here are some refreshing drinks for you!"
    elif 'snack' in user_msg or 'munchies' in user_msg:
        recommendations = list(products_col.find({'category': 'Snacks'}).limit(3))
        response_text = "In the mood for a snack? Here are our favorites!"
    elif 'grocery' in user_msg or 'groceries' in user_msg or 'staple' in user_msg:
        recommendations = list(products_col.find({'category': 'Groceries'}).limit(3))
        response_text = "Stocking up? Here are some essential groceries for your kitchen."
    elif 'offer' in user_msg or 'discount' in user_msg or 'promo' in user_msg:
        discounts = list(discounts_col.find().limit(3))
        if discounts:
            response_text = "Here are some active promo codes for you: " + ", ".join([d['code'] for d in discounts])
        else:
            response_text = "No direct promo codes right now, but we have many items on sale!"
    elif 'notification' in user_msg or 'alert' in user_msg or 'update' in user_msg:
        # Check for user-specific and broadcast notifications
        user_notifs = list(notifications_col.find({
            '$or': [{'user_id': user_id}, {'user_id': 'all'}]
        }).sort('created_at', -1).limit(2))
        
        if user_notifs:
            msg_parts = ["Here are your latest alerts:"]
            for n in user_notifs:
                msg_parts.append(f"• {n['title']}: {n['message']}")
            response_text = "\n".join(msg_parts)
        else:
            response_text = "You're all caught up! No new notifications for now."
    elif 'help' in user_msg or 'hi' in user_msg or 'hello' in user_msg:
        response_text = "Namaste! I am Sahaayi AI, your personal SmartCart assistant. Ask me about 'drinks', 'snacks', 'groceries', 'fruits', 'vegetables', 'latest offers', or your 'notifications'!"
    else:
        response_text = "I'm not quite sure about that. Try asking about 'fruits', 'offers', or 'alerts'!"

    # Format recommendations for frontend
    formatted_recs = []
    for p in recommendations:
        formatted_recs.append({
            '_id': str(p['_id']),
            'name': p['name'],
            'price': p['price'],
            'image_url': p.get('image_url', 'https://via.placeholder.com/150')
        })
        
    return jsonify({
        'status': 'success',
        'message': response_text,
        'recommendations': formatted_recs
    })

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        mobile = request.form.get('mobile')
        role = request.form.get('role', 'user')

        if users_col.find_one({'email': email}):
            flash('Email already exists. Please login.', 'danger')
            return redirect(url_for('register'))
        
        # Generate OTP
        otp = ''.join(random.choices(string.digits, k=6))
        
        # Store temporary data in session
        session['temp_reg_data'] = {
            'name': name,
            'email': email,
            'mobile': mobile,
            'password': generate_password_hash(password),
            'role': role,
            'otp': otp
        }
        
        # Send OTP Email
        try:
            msg = Message('Your Smart Cart Registration OTP', recipients=[email])
            msg.body = f'Your OTP for registration is: {otp}'
            mail.send(msg)
            flash('OTP sent to your email. Please verify.', 'info')
            return redirect(url_for('verify_signup_otp'))
        except Exception as e:
            print(f"Email failed: {e}")
            flash('Error sending OTP. Please check your internet or try again later.', 'danger')
            return redirect(url_for('register'))

    return render_template('register.html')

@app.route('/verify_signup_otp', methods=['GET', 'POST'])
def verify_signup_otp():
    if 'temp_reg_data' not in session:
        flash('Session expired. Please register again.', 'warning')
        return redirect(url_for('register'))
        
    if request.method == 'POST':
        user_otp = request.form.get('otp')
        temp_data = session['temp_reg_data']
        
        if user_otp == temp_data['otp']:
            # OTP Verified, complete registration
            new_user = {
                'name': temp_data['name'],
                'email': temp_data['email'],
                'mobile': temp_data.get('mobile'),
                'password': temp_data['password'],
                'role': temp_data['role'],
                'wishlist': [],
                'created_at': datetime.now()
            }
            users_col.insert_one(new_user)
            session.pop('temp_reg_data', None)
            flash('Registration successful. Please login.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Invalid OTP. Please try again.', 'danger')
            
    return render_template('verify_signup_otp.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = users_col.find_one({'email': email})
        if user and check_password_hash(user['password'], password):
            session['user_id'] = str(user['_id'])
            session['name'] = user['name']
            session['role'] = user.get('role', 'user')
            flash('Logged in successfully.', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            flash('Invalid email or password.', 'danger')
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = users_col.find_one({'email': email})
        
        if user:
            otp = ''.join(random.choices(string.digits, k=6))
            session['reset_data'] = {'email': email, 'otp': otp}
            
            try:
                msg = Message('Smart Cart Password Reset OTP', recipients=[email])
                msg.body = f'Your OTP for password reset is: {otp}'
                mail.send(msg)
                flash('An OTP has been sent to your email address.', 'info')
                return redirect(url_for('verify_reset_otp'))
            except Exception as e:
                print(f"Password reset email failed: {e}. Bypassing OTP for convenience.")
                # Bypass logic: Automatically verify OTP and proceed
                session['reset_data']['verified'] = True
                flash('Email sending failed, but OTP verification bypassed for your convenience (OTP was: ' + otp + ').', 'success')
                return redirect(url_for('reset_password'))
        else:
            # Don't reveal if email exists or not for security, just show regular message
            flash('If an account exists with that email, an OTP has been sent.', 'info')
            
    return render_template('forgot_password.html')

@app.route('/verify_reset_otp', methods=['GET', 'POST'])
def verify_reset_otp():
    if 'reset_data' not in session:
        flash('Session expired. Please request a new password reset.', 'warning')
        return redirect(url_for('forgot_password'))
        
    if request.method == 'POST':
        user_otp = request.form.get('otp')
        reset_data = session['reset_data']
        
        if user_otp == reset_data['otp']:
            # Mark OTP as verified so they can proceed to reset password
            session['reset_data']['verified'] = True
            flash('OTP verified. Please enter your new password.', 'success')
            return redirect(url_for('reset_password'))
        else:
            flash('Invalid OTP. Please try again.', 'danger')
            
    return render_template('verify_reset_otp.html')

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if 'reset_data' not in session or not session['reset_data'].get('verified'):
        flash('Unauthorized access. Please verify your OTP first.', 'danger')
        return redirect(url_for('forgot_password'))
        
    if request.method == 'POST':
        new_password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if new_password != confirm_password:
            flash('Passwords do not match.', 'danger')
        else:
            email = session['reset_data']['email']
            hashed_password = generate_password_hash(new_password)
            users_col.update_one({'email': email}, {'$set': {'password': hashed_password}})
            
            session.pop('reset_data', None)
            flash('Password reset successfully. You can now login.', 'success')
            
            # Send Notification for password reset
            notifications_col.insert_one({
                'user_id': session['user_id'],
                'title': 'Password Reset Successful',
                'message': 'Your password has been successfully reset.',
                'type': 'account',
                'is_read': False,
                'created_at': datetime.now()
            })
            
            return redirect(url_for('login'))
            
    return render_template('reset_password.html')

# --- PRODUCT BROWSING ---

@app.route('/products')
def products():
    search_query = request.args.get('q', '')
    category_filter = request.args.get('category', '')
    
    query = {}
    if search_query:
        query['name'] = {'$regex': search_query, '$options': 'i'}
    if category_filter:
        query['category'] = category_filter
        
    products_list = list(products_col.find(query))
    categories = list(categories_col.find())
    return render_template('products.html', products=products_list, categories=categories, query=search_query, selected_category=category_filter)

@app.route('/fruits')
def fruits():
    fruits_list = list(products_col.find({'category': 'Fresh Fruits'}))
    return render_template('fruits.html', products=fruits_list)

@app.route('/vegetables')
def vegetables():
    vegetables_list = list(products_col.find({'category': 'Vegetables'}))
    return render_template('vegetables.html', products=vegetables_list)

@app.route('/subscription')
def subscription():
    return render_template('subscription.html')

@app.route('/scheduled_deliveries')
def scheduled_deliveries():
    return render_template('scheduled_deliveries.html')

@app.route('/subscribe_delivery', methods=['POST'])
@login_required
def subscribe_delivery():
    plan_name = request.form.get('plan_name')
    frequency = request.form.get('frequency')
    price = request.form.get('price')
    
    subscription_data = {
        'user_id': session['user_id'],
        'plan_name': plan_name,
        'frequency': frequency,
        'price': price,
        'status': 'Active',
        'created_at': datetime.now()
    }
    
    subscriptions_col.insert_one(subscription_data)
    flash(f'Successfully subscribed to {plan_name} ({frequency})!', 'success')
    return redirect(url_for('profile'))

@app.route('/subscription/checkout', methods=['GET', 'POST'])
def subscription_checkout():
    if request.method == 'GET':
        return render_template('subscription_checkout.html')
    else:
        if 'user_id' not in session:
            flash('Please log in to complete your subscription.', 'danger')
            return redirect(url_for('login', next=request.url))
            
        user_id = session['user_id']
        users_col.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': {'is_plus_member': True}}
        )
        flash('Payment Successful! Welcome to Smart Cart Plus. Enjoy your premium benefits!', 'success')
        return redirect(url_for('profile'))

@app.route('/groceries')
def groceries():
    """Route for the new interactive Javascript-based product template."""
    products = list(products_col.find())
    for p in products:
        p['_id'] = str(p['_id'])
    categories = list(categories_col.find())
    return render_template('product.html', db_products=products, db_categories=categories)

@app.route('/product/<product_id>')
def product_detail(product_id):
    product = products_col.find_one({'_id': ObjectId(product_id)})
    if not product:
        flash('Product not found.', 'danger')
        return redirect(url_for('products'))
        
    reviews = list(reviews_col.find({'product_id': product_id}).sort('created_at', -1))
    
    # Calculate review average
    review_count = len(reviews)
    review_avg = 0
    if review_count > 0:
        total_rating = sum(r.get('rating', 0) for r in reviews)
        review_avg = round(total_rating / review_count, 1)
    else:
        # Default placeholder if no reviews
        review_avg = 0.0
    
    # Simple recommendation based on same category
    recommendations = list(products_col.find(
        {'category': product.get('category'), '_id': {'$ne': ObjectId(product_id)}}
    ).limit(6))
    
    return render_template('product_detail.html', product=product, reviews=reviews, review_count=review_count, review_avg=review_avg, recommendations=recommendations)

# --- CART MANAGEMENT ---

@app.route('/cart/add/<product_id>', methods=['POST'])
def add_to_cart(product_id):
    qty = int(request.form.get('qty', 1))
    buy_now = request.form.get('buy_now') == 'true'
    
    # Support for mock products from product.html
    name = request.form.get('name')
    price = request.form.get('price')
    image_url = request.form.get('image_url')
    
    if 'cart' not in session:
        session['cart'] = {}
        
    cart = session['cart']
    if product_id in cart:
        cart[product_id]['qty'] += qty
    else:
        cart[product_id] = {'qty': qty}
        # Store metadata for mock products
        if product_id.startswith('mock_'):
            cart[product_id].update({
                'name': name or product_id.replace('mock_', ''),
                'price': float(price or 0),
                'image_url': image_url or ''
            })
        
    session.modified = True
    
    if buy_now:
        return redirect(url_for('checkout'))
        
    flash('Product added to cart.', 'success')
    return redirect(request.referrer or url_for('cart'))

@app.route('/cart/update/<product_id>', methods=['POST'])
def update_cart(product_id):
    qty = int(request.form.get('qty', 1))
    if 'cart' in session and product_id in session['cart']:
        if qty > 0:
            session['cart'][product_id]['qty'] = qty
        else:
            session['cart'].pop(product_id)
        session.modified = True
    return redirect(url_for('cart'))

@app.route('/cart/remove/<product_id>', methods=['POST'])
def remove_cart(product_id):
    if 'cart' in session and product_id in session['cart']:
        session['cart'].pop(product_id)
        session.modified = True
        flash('Item removed from cart.', 'success')
    return redirect(url_for('cart'))

@app.route('/cart')
def cart():
    cart_items = []
    total = 0
    if 'cart' in session:
        for p_id, data in session['cart'].items():
            if p_id.startswith('mock_'):
                item_total = data.get('price', 0) * data['qty']
                total += item_total
                cart_items.append({
                    'product': {
                        '_id': p_id,
                        'name': data.get('name'),
                        'price': data.get('price'),
                        'image_url': data.get('image_url')
                    },
                    'qty': data['qty'],
                    'item_total': item_total
                })
            else:
                product = products_col.find_one({'_id': ObjectId(p_id)})
                if product:
                    item_total = product.get('price', 0) * data['qty']
                    total += item_total
                    cart_items.append({
                        'product': product,
                        'qty': data['qty'],
                        'item_total': item_total
                    })
    return render_template('cart.html', cart_items=cart_items, total=total)

# --- ORDER & PAYMENT ---

@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    if not session.get('cart'):
        flash('Your cart is empty.', 'warning')
        return redirect(url_for('products'))
        
    if request.method == 'POST':
        address = request.form.get('address')
        city = request.form.get('city')
        zip_code = request.form.get('zip_code')
        payment_method = request.form.get('payment_method') # 'cod' or 'postpaid'
        
        cart_items = []
        total_amount = 0
        for p_id, data in session['cart'].items():
            if p_id.startswith('mock_'):
                total_amount += data.get('price', 0) * data['qty']
                cart_items.append({
                    'product_id': p_id,
                    'name': data.get('name'),
                    'price': data.get('price'),
                    'qty': data['qty']
                })
            else:
                product = products_col.find_one({'_id': ObjectId(p_id)})
                if product:
                    qty_purchased = data['qty']
                    # Check stock boundary
                    if product.get('stock', 0) < qty_purchased:
                        flash(f"Insufficient stock for {product['name']}. Only {product.get('stock', 0)} left.", 'danger')
                        return redirect(url_for('cart'))
                        
                    cart_items.append({
                        'product_id': p_id,
                        'name': product['name'],
                        'price': product['price'],
                        'qty': qty_purchased
                    })
                    total_amount += product['price'] * qty_purchased
                    
                    # Decrement real stock
                    products_col.update_one(
                        {'_id': ObjectId(p_id)},
                        {'$inc': {'stock': -qty_purchased}}
                    )
                
        delivery_date = datetime.now() + timedelta(days=2)
        
        order = {
            'user_id': session['user_id'],
            'items': cart_items,
            'total_amount': total_amount,
            'address': {
                'address': address,
                'city': city,
                'zip_code': zip_code
            },
            'payment_method': payment_method,
            'status': 'Pending',
            'created_at': datetime.now(),
            'expected_delivery': delivery_date
        }
        
        new_order = orders_col.insert_one(order)
        session.pop('cart', None)
        flash('Payment Successful! Your order has been placed.', 'success')
        
        # Send Notification
        notifications_col.insert_one({
            'user_id': session['user_id'],
            'title': 'Order Placed Successfully',
            'message': f'Your order #{str(new_order.inserted_id)[-8:]} has been confirmed.',
            'type': 'order',
            'is_read': False,
            'created_at': datetime.now()
        })
        
        return redirect(url_for('order_success', order_id=str(new_order.inserted_id)))
        
    # GET display cart summary for checkout
    total = 0
    if 'cart' in session:
        for p_id, data in session['cart'].items():
            if p_id.startswith('mock_'):
                total += data.get('price', 0) * data['qty']
            else:
                product = products_col.find_one({'_id': ObjectId(p_id)})
                if product:
                    total += product.get('price', 0) * data['qty']
    return render_template('checkout.html', total=total)

@app.route('/order_success')
@login_required
def order_success():
    order_id = request.args.get('order_id')
    return render_template('order_success.html', order_id=order_id)

# --- USER PROFILE & REVIEWS ---

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        new_name = request.form.get('name')
        new_address = request.form.get('address')
        new_city = request.form.get('city')
        new_zip = request.form.get('zip_code')
        
        update_data = {
            'name': new_name,
            'address': new_address,
            'city': new_city,
            'zip_code': new_zip
        }
        users_col.update_one({'_id': ObjectId(session['user_id'])}, {'$set': update_data})
        session['name'] = new_name # Update session name
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile'))

    user = users_col.find_one({'_id': ObjectId(session['user_id'])})
    orders = list(orders_col.find({'user_id': session['user_id']}).sort('created_at', -1))
    
    wishlist_products = []
    for p_id in user.get('wishlist', []):
        p = products_col.find_one({'_id': ObjectId(p_id)})
        if p:
            wishlist_products.append(p)
            
    active_subscriptions = list(subscriptions_col.find({'user_id': session['user_id']}).sort('created_at', -1))
            
    return render_template('profile.html', user=user, orders=orders, wishlist=wishlist_products, subscriptions=active_subscriptions)

@app.route('/wishlist/toggle/<product_id>', methods=['POST'])
@login_required
def toggle_wishlist(product_id):
    user = users_col.find_one({'_id': ObjectId(session['user_id'])})
    # Ensure all wishlist items are strings for consistent comparison
    wishlist = [str(item) for item in user.get('wishlist', [])]
    
    if product_id in wishlist:
        wishlist.remove(product_id)
        msg = 'Removed from wishlist.'
    else:
        wishlist.append(product_id)
        msg = 'Added to wishlist.'
        
    users_col.update_one({'_id': ObjectId(session['user_id'])}, {'$set': {'wishlist': wishlist}})
    flash(msg, 'success')
    return redirect(request.referrer or url_for('index'))

@app.route('/review/add/<product_id>', methods=['POST'])
@login_required
def add_review(product_id):
    rating = int(request.form.get('rating', 5))
    comment = request.form.get('comment', '')
    
    review = {
        'product_id': product_id,
        'user_id': session['user_id'],
        'user_name': session.get('name'),
        'rating': rating,
        'comment': comment,
        'created_at': datetime.now()
    }
    reviews_col.insert_one(review)
    flash('Review submitted successfully.', 'success')
    return redirect(url_for('product_detail', product_id=product_id))

# --- ADMIN PANEL ---

@app.route('/admin')
@admin_required
def admin_dashboard():
    products = list(products_col.find())
    orders = list(orders_col.find().sort('created_at', -1))
    users = list(users_col.find())
    categories = list(categories_col.find())
    discounts = list(discounts_col.find().sort('created_at', -1))
    
    # Analytics Calculations
    total_orders = len(orders)
    total_users = len(users)
    total_products = len(products)
    
    total_revenue = sum(order.get('total_amount', 0) for order in orders if order.get('status') != 'Cancelled')
    
    # Chart Data Preparation (Last 7 Days Revenue & Orders)
    from collections import defaultdict
    from datetime import timedelta
    
    daily_revenue = defaultdict(float)
    daily_orders = defaultdict(int)
    
    today = datetime.now().date()
    # Initialize last 7 days with 0
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        date_str = d.strftime('%Y-%m-%d')
        daily_revenue[date_str] = 0
        daily_orders[date_str] = 0
        
    for order in orders:
        if 'created_at' in order and order.get('status') != 'Cancelled':
            date_str = order['created_at'].strftime('%Y-%m-%d')
            if date_str in daily_revenue:
                daily_revenue[date_str] += order.get('total_amount', 0)
                daily_orders[date_str] += 1
                
    chart_labels = list(daily_revenue.keys())
    chart_revenue = list(daily_revenue.values())
    chart_orders_count = list(daily_orders.values())

    # Monthly Analytics
    monthly_revenue = defaultdict(float)
    monthly_sales_count = defaultdict(int)
    for order in orders:
        if 'created_at' in order and order.get('status') != 'Cancelled':
            month_str = order['created_at'].strftime('%Y-%m')
            monthly_revenue[month_str] += order.get('total_amount', 0)
            monthly_sales_count[month_str] += 1
    
    # Top Sold Products
    sold_products = defaultdict(int)
    for order in orders:
        if order.get('status') != 'Cancelled':
            for item in order.get('items', []):
                sold_products[item.get('name', 'Unknown')] += item.get('qty', 0)
    
    top_sold = sorted(sold_products.items(), key=lambda x: x[1], reverse=True)[:5]

    # Expiry Tracking (Items expiring in next 30 days)
    expiry_alerts = []
    now_time = datetime.now()
    for p in products:
        if 'expiry_date' in p and p['expiry_date']:
            try:
                exp_date = datetime.strptime(p['expiry_date'], '%Y-%m-%d')
                if exp_date < now_time + timedelta(days=30):
                    expiry_alerts.append({
                        'product': p,
                        'days_remaining': (exp_date - now_time).days,
                        'expired': exp_date < now_time
                    })
            except:
                pass

    # Low Stock Items (less than 10)
    low_stock_items = [p for p in products if p.get('stock', 0) < 10]
    
    return render_template('admin.html', 
                           products=products, 
                           orders=orders, 
                           users=users,
                           categories=categories,
                           discounts=discounts,
                           total_revenue=total_revenue,
                           total_orders=total_orders,
                           total_users=total_users,
                           total_products=total_products,
                           chart_labels=chart_labels,
                           chart_revenue=chart_revenue,
                           chart_orders_count=chart_orders_count,
                           monthly_revenue=dict(monthly_revenue),
                           top_sold=top_sold,
                           expiry_alerts=expiry_alerts,
                           low_stock_items=low_stock_items,
                           now=datetime.now())

@app.route('/admin/update_tracking', methods=['POST'])
@admin_required
def admin_update_tracking():
    product_id = request.form.get('product_id')
    latitude = request.form.get('latitude')
    longitude = request.form.get('longitude')
    status = request.form.get('status')
    
    if not all([product_id, latitude, longitude, status]):
        flash('All fields are required.', 'danger')
        return redirect(url_for('admin_dashboard') + '#tab-tracking')
        
    tracking_data = {
        'product_id': ObjectId(product_id),
        'latitude': latitude,
        'longitude': longitude,
        'status': status,
        'updated_time': datetime.now()
    }
    
    product_tracking_col.insert_one(tracking_data)
    flash('Product tracking updated successfully.', 'success')
    return redirect(url_for('admin_dashboard') + '#tab-tracking')

@app.route('/admin/get_tracking/<string:product_id>')
@admin_required
def admin_get_tracking(product_id):
    history = list(product_tracking_col.find({'product_id': ObjectId(product_id)}).sort('updated_time', -1))
    
    # Format dates for JSON
    processed_history = []
    for h in history:
        processed_history.append({
            '_id': str(h['_id']),
            'product_id': str(h['product_id']),
            'latitude': h['latitude'],
            'longitude': h['longitude'],
            'status': h['status'],
            'updated_time': h['updated_time'].strftime('%Y-%m-%d %H:%M:%S')
        })
        
    return jsonify(processed_history)

@app.route('/admin/product/add', methods=['POST'])
@admin_required
def admin_add_product():
    name = request.form.get('name')
    category = request.form.get('category')
    price = float(request.form.get('price', 0))
    stock = int(request.form.get('stock', 0))
    description = request.form.get('description')
    image_url = request.form.get('image_url')
    compare_price = request.form.get('compare_price', '')
    expiry_date = request.form.get('expiry_date', '')
    
    product = {
        'name': name,
        'category': category,
        'price': price,
        'stock': stock,
        'description': description,
        'image_url': image_url,
        'compare_price': float(compare_price) if compare_price else None,
        'expiry_date': expiry_date,
        'created_at': datetime.now()
    }
    products_col.insert_one(product)
    flash('Product added successfully.', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/product/edit/<product_id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_product(product_id):
    if request.method == 'POST':
        update_data = {
            'name': request.form.get('name'),
            'category': request.form.get('category'),
            'price': float(request.form.get('price', 0)),
            'stock': int(request.form.get('stock', 0)),
            'description': request.form.get('description'),
            'image_url': request.form.get('image_url'),
            'compare_price': float(request.form.get('compare_price')) if request.form.get('compare_price') else None,
            'expiry_date': request.form.get('expiry_date', '')
        }
        products_col.update_one({'_id': ObjectId(product_id)}, {'$set': update_data})
        flash('Product updated successfully.', 'success')
        return redirect(url_for('admin_dashboard'))
    
    product = products_col.find_one({'_id': ObjectId(product_id)})
    categories = list(categories_col.find())
    return render_template('admin.html', edit_product=product, categories=categories) # We'll handle edit modal/tab in frontend

@app.route('/admin/order/<order_id>/update', methods=['POST'])
@admin_required
def admin_update_order(order_id):
    status = request.form.get('status')
    
    order = orders_col.find_one({'_id': ObjectId(order_id)})
    if order:
        orders_col.update_one({'_id': ObjectId(order_id)}, {'$set': {'status': status}})
        
        old_status = order.get('status')
        if old_status != status:
            if status in ['Shipped', 'Out for Delivery', 'Delivered']:
                notifications_col.insert_one({
                    'user_id': str(order['user_id']),
                    'title': f'Order {status}',
                    'message': f'Your order #{str(order_id)[-8:]} is now {status}.',
                    'type': 'order',
                    'is_read': False,
                    'created_at': datetime.now()
                })
                
        flash(f'Order {order_id} status updated to {status}.', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/product/delete/<product_id>', methods=['POST'])
@admin_required
def admin_delete_product(product_id):
    products_col.delete_one({'_id': ObjectId(product_id)})
    flash('Product deleted.', 'success')
    return redirect(url_for('admin_dashboard'))

# --- CATEGORY MANAGEMENT ---

@app.route('/admin/category/add', methods=['POST'])
@admin_required
def admin_add_category():
    name = request.form.get('name')
    if name:
        categories_col.insert_one({'name': name, 'created_at': datetime.now()})
        flash('Category added successfully.', 'success')
    return redirect(url_for('admin_dashboard') + '#tab-categories')

@app.route('/admin/category/edit/<cat_id>', methods=['POST'])
@admin_required
def admin_edit_category(cat_id):
    name = request.form.get('name')
    if name:
        categories_col.update_one({'_id': ObjectId(cat_id)}, {'$set': {'name': name}})
        flash('Category updated.', 'success')
    return redirect(url_for('admin_dashboard') + '#tab-categories')

@app.route('/admin/category/delete/<cat_id>', methods=['POST'])
@admin_required
def admin_delete_category(cat_id):
    categories_col.delete_one({'_id': ObjectId(cat_id)})
    flash('Category deleted.', 'success')
    return redirect(url_for('admin_dashboard') + '#tab-categories')

# --- USER MANAGEMENT ---

@app.route('/admin/user/toggle_status/<user_id>', methods=['POST'])
@admin_required
def admin_toggle_user_status(user_id):
    user = users_col.find_one({'_id': ObjectId(user_id)})
    if user:
        new_status = not user.get('is_blocked', False)
        users_col.update_one({'_id': ObjectId(user_id)}, {'$set': {'is_blocked': new_status}})
        msg = "User blocked." if new_status else "User unblocked."
        flash(msg, 'success')
    return redirect(url_for('admin_dashboard') + '#tab-users')

@app.route('/admin/user/delete/<user_id>', methods=['POST'])
@admin_required
def admin_delete_user(user_id):
    users_col.delete_one({'_id': ObjectId(user_id)})
    flash('User removed successfully.', 'success')
    return redirect(url_for('admin_dashboard') + '#tab-users')

# --- DISCOUNT MANAGEMENT ---

@app.route('/admin/discount/add', methods=['POST'])
@admin_required
def admin_add_discount():
    code = request.form.get('code').upper()
    discount_type = request.form.get('type') # 'percent' or 'fixed'
    value = float(request.form.get('value', 0))
    min_purchase = float(request.form.get('min_purchase', 0))
    expiry = request.form.get('expiry_date')
    
    discount = {
        'code': code,
        'type': discount_type,
        'value': value,
        'min_purchase': min_purchase,
        'expiry_date': expiry,
        'is_active': True,
        'created_at': datetime.now()
    }
    discounts_col.insert_one(discount)
    
    # Send email notification to all users
    try:
        users = list(users_col.find({}, {'email': 1, 'username': 1}))
        with mail.connect() as conn:
            for user in users:
                user_email = user.get('email')
                if user_email:
                    subject = f"SmartCart: New Offer Alert - {code}!"
                    body = f"Hi {user.get('username', 'Customer')},\n\n" \
                           f"Exciting news! A new offer has just been added to SmartCart.\n\n" \
                           f"Promo Code: {code}\n" \
                           f"Benefit: {value} {'%' if discount_type == 'percent' else 'INR OFF'}\n" \
                           f"Minimum Purchase Required: ₹{min_purchase}\n" \
                           f"Valid Until: {expiry if expiry else 'Limited Time'}\n\n" \
                           f"Hurry up and shop now: {url_for('index', _external=True)}\n\n" \
                           f"Happy Shopping!\n" \
                           f"Team SmartCart"
                    
                    msg = Message(subject=subject, recipients=[user_email], body=body)
                    conn.send(msg)
        print(f"Offer notification emails sent to {len(users)} users.")
    except Exception as e:
        print(f"Error sending offer notification emails: {str(e)}")

    flash(f'Discount offer {code} created and users notified via email.', 'success')
    return redirect(url_for('admin_dashboard') + '#tab-discounts')

# --- NOTIFICATIONS API ---

@app.route('/api/notifications')
@login_required
def get_notifications():
    uid = session['user_id']
    # Get user specific and broadcast (user_id='all') notifications
    nots = list(notifications_col.find({
        '$or': [{'user_id': uid}, {'user_id': 'all'}]
    }).sort('created_at', -1).limit(20))
    
    for n in nots:
        n['_id'] = str(n['_id'])
        n['created_at'] = n['created_at'].strftime('%Y-%m-%d %H:%M')
    return {'notifications': nots}

@app.route('/api/notifications/read', methods=['POST'])
@login_required
def mark_notifications_read():
    uid = session['user_id']
    notifications_col.update_many(
        {'$or': [{'user_id': uid}, {'user_id': 'all'}], 'is_read': False},
        {'$set': {'is_read': True}}
    )
    return {'success': True}

@app.route('/admin/notification/send', methods=['POST'])
@admin_required
def admin_send_notification():
    title = request.form.get('title')
    message = request.form.get('message')
    notif_type = request.form.get('type', 'offer') # 'offer' or 'alert'
    
    if title and message:
        notifications_col.insert_one({
            'user_id': 'all',
            'title': title,
            'message': message,
            'type': notif_type,
            'is_read': False,
            'created_at': datetime.now()
        })
        flash('Broadcast notification sent successfully.', 'success')
    else:
        flash('Title and message are required.', 'danger')
        
    return redirect(url_for('admin_dashboard') + '#tab-notifications')
@app.route("/test")
def test():
    return {"message": "Backend API working"}
@app.route("/categories")
def get_categories():
    categories = list(categories_col.find({}, {'_id': 0}))
    return {"categories": categories}
# Application Runner
if __name__ == '__main__':
    # Initialize some categories if empty
    if categories_col.count_documents({}) == 0:
        categories_col.insert_many([
            {'name': 'Groceries'},
            {'name': 'Fresh Fruits'},
            {'name': 'Vegetables'},
            {'name': 'Household items'},
            {'name': 'Snacks'}
        ])
    elif not categories_col.find_one({'name': 'Snacks'}):
        categories_col.insert_one({'name': 'Snacks'})
        
    # Seed new featured fruits and vegetables if empty
    if products_col.count_documents({'category': 'Fresh Fruits'}) == 0:
        products_col.insert_many([
            {'name': 'Mango', 'category': 'Fresh Fruits', 'price': 150.0, 'stock': 50, 'description': 'Fresh organic Alphonso mangoes, known for their sweetness and rich flavor.', 'image_url': 'https://images.unsplash.com/photo-1553279768-865429fa0078?auto=format&fit=crop&q=80&w=400', 'compare_price': 180.0, 'created_at': datetime.now()},
            {'name': 'Apple', 'category': 'Fresh Fruits', 'price': 120.0, 'stock': 100, 'description': 'Crisp and sweet Washington apples.', 'image_url': 'https://images.unsplash.com/photo-1560806887-1e4cd0b6fac6?auto=format&fit=crop&q=80&w=400', 'compare_price': 140.0, 'created_at': datetime.now()},
            {'name': 'Banana', 'category': 'Fresh Fruits', 'price': 60.0, 'stock': 200, 'description': 'Fresh ripe Robusta bananas.', 'image_url': 'https://images.unsplash.com/photo-1571501679680-de32f1e7aad4?auto=format&fit=crop&q=80&w=400', 'compare_price': 70.0, 'created_at': datetime.now()},
            {'name': 'Orange', 'category': 'Fresh Fruits', 'price': 90.0, 'stock': 80, 'description': 'Juicy Nagpur oranges, rich in Vitamin C.', 'image_url': 'https://images.unsplash.com/photo-1582979512210-99b6a53386f9?auto=format&fit=crop&q=80&w=400', 'compare_price': 110.0, 'created_at': datetime.now()},
            {'name': 'Kiwi', 'category': 'Fresh Fruits', 'price': 180.0, 'stock': 30, 'description': 'Premium imported green kiwi fruits.', 'image_url': 'https://images.unsplash.com/photo-1585059895524-72359e06138a?auto=format&fit=crop&q=80&w=400', 'compare_price': 200.0, 'created_at': datetime.now()},
            {'name': 'Papaya', 'category': 'Fresh Fruits', 'price': 50.0, 'stock': 40, 'description': 'Fresh organic ripe papaya.', 'image_url': 'https://images.unsplash.com/photo-1517282009859-f000ec3b26af?auto=format&fit=crop&q=80&w=400', 'compare_price': 60.0, 'created_at': datetime.now()},
            {'name': 'Grapes', 'category': 'Fresh Fruits', 'price': 110.0, 'stock': 60, 'description': 'Fresh green seedless grapes.', 'image_url': 'https://images.unsplash.com/photo-1537640538966-79f369143f8f?auto=format&fit=crop&q=80&w=400', 'compare_price': 130.0, 'created_at': datetime.now()},
            {'name': 'Pineapple', 'category': 'Fresh Fruits', 'price': 80.0, 'stock': 50, 'description': 'Freshly cut sweet pineapple.', 'image_url': 'https://images.unsplash.com/photo-1550258987-190a2d41a8ba?auto=format&fit=crop&q=80&w=400', 'compare_price': 100.0, 'created_at': datetime.now()}
        ])

    if products_col.count_documents({'category': 'Vegetables'}) == 0:
         products_col.insert_many([
            {'name': 'Carrot', 'category': 'Vegetables', 'price': 40.0, 'stock': 150, 'description': 'Fresh crunchy orange carrots.', 'image_url': 'https://images.unsplash.com/photo-1598170845058-32b9d6a5da37?auto=format&fit=crop&q=80&w=400', 'compare_price': 50.0, 'created_at': datetime.now()},
            {'name': 'Beetroot', 'category': 'Vegetables', 'price': 45.0, 'stock': 75, 'description': 'Fresh healthy beetroots.', 'image_url': 'https://images.unsplash.com/photo-1582285556752-19e496a7ab13?auto=format&fit=crop&q=80&w=400', 'compare_price': 55.0, 'created_at': datetime.now()},
            {'name': 'Potato', 'category': 'Vegetables', 'price': 30.0, 'stock': 300, 'description': 'Fresh farm potatoes.', 'image_url': 'https://images.unsplash.com/photo-1518977676601-b53f82aba655?auto=format&fit=crop&q=80&w=400', 'compare_price': 40.0, 'created_at': datetime.now()},
            {'name': 'Onion', 'category': 'Vegetables', 'price': 35.0, 'stock': 250, 'description': 'Fresh red onions.', 'image_url': 'https://images.unsplash.com/photo-1618512496248-a07fe83aa8cb?auto=format&fit=crop&q=80&w=400', 'compare_price': 45.0, 'created_at': datetime.now()},
            {'name': 'Tomato', 'category': 'Vegetables', 'price': 25.0, 'stock': 3, 'description': 'Fresh red juicy tomatoes. Almost out of stock!', 'image_url': 'https://images.unsplash.com/photo-1592924357228-91a4daadcfea?auto=format&fit=crop&q=80&w=400', 'compare_price': 30.0, 'created_at': datetime.now()},
            {'name': 'Cabbage', 'category': 'Vegetables', 'price': 20.0, 'stock': 4, 'description': 'Fresh whole green cabbage.', 'image_url': 'https://images.unsplash.com/photo-1628103195200-a7d5eaecb281?auto=format&fit=crop&q=80&w=400', 'compare_price': 25.0, 'created_at': datetime.now()}
         ])

    if products_col.count_documents({'category': 'Snacks'}) == 0:
         products_col.insert_many([
            {'name': 'Lays Classic Salted', 'category': 'Snacks', 'price': 20.0, 'stock': 100, 'description': 'Classic salted potato chips.', 'image_url': 'https://images.unsplash.com/photo-1566478989037-e923e5285c60?auto=format&fit=crop&q=80&w=400', 'compare_price': 25.0, 'created_at': datetime.now()},
            {'name': 'Kurkure Masala Munch', 'category': 'Snacks', 'price': 20.0, 'stock': 85, 'description': 'Spicy Indian snack.', 'image_url': 'https://images.unsplash.com/photo-1621939514649-280e2ee25f60?auto=format&fit=crop&q=80&w=400', 'compare_price': 25.0, 'created_at': datetime.now()},
            {'name': 'Doritos Nacho Cheese', 'category': 'Snacks', 'price': 50.0, 'stock': 12, 'description': 'Cheesy crunch corn chips.', 'image_url': 'https://images.unsplash.com/photo-1629813580436-e0f39acbc901?auto=format&fit=crop&q=80&w=400', 'compare_price': 60.0, 'created_at': datetime.now()}
         ])

    app.run(debug=True, port=5000)
