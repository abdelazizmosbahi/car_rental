from datetime import datetime
from bson import ObjectId
from flask import Flask, flash, request, jsonify, render_template
from models import add_contact, add_testimonial, get_all_cars
from models import add_car, cars_collection, get_renters_with_rented_cars,get_non_rented_cars, delete_car, update_car, get_car_by_id, get_all_cars, rent_car
from flask import request, render_template, redirect, url_for
import base64
from pymongo import MongoClient
from flask import session, jsonify, render_template, request, redirect, url_for

app = Flask(__name__)
app.secret_key = 'c8c40dba715a170e1b8d094200273e12' 

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['car_rental_db']  # The database for the car rental app
cars_collection = db['voitures']
tenants_collection = db['tenant']  # New tenants collection
testimonials_collection = db.testimonials  # Collection for contact us messages
contact_us_collection = db.contact_us  # Collection for contact us messages

@app.route('/')
def index():
    cars = list(cars_collection.find())
    today = datetime.now()
    for car in cars:
        start_date_str = car.get('start_date')  # Using .get() to avoid KeyError
        end_date_str = car.get('end_date')

        # If the start_date or end_date are present, convert them to datetime objects
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d') if start_date_str else None
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d') if end_date_str else None
        
        if car['etat'] == 0:
            car['status'] = 'available'
            car['status_message'] = "Available"
            car['status_color'] = "text-success"
        elif start_date and today < start_date:
            car['status'] = 'available_until'
            car['status_message'] = f"Available on {start_date.strftime('%Y-%m-%d')}"
            car['status_color'] = "text-gray"
        elif end_date and today > end_date and car['etat'] != 0:
            car['status'] = 'not_returned'
            car['status_message'] = "Not returned yet"
            car['status_color'] = "text-danger"
        elif start_date and end_date and start_date <= today <= end_date:
            car['status'] = 'rented'
            car['status_message'] = f"Rented until {end_date.strftime('%Y-%m-%d')}"
            car['status_color'] = "text-warning"
    return render_template('index.html', cars=cars)


@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/blog')
def blog():
    return render_template('blog.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/listing')
def listing():
    cars = list(cars_collection.find())
    today = datetime.now()
    for car in cars:
        start_date_str = car.get('start_date')  # Using .get() to avoid KeyError
        end_date_str = car.get('end_date')

        # If the start_date or end_date are present, convert them to datetime objects
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d') if start_date_str else None
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d') if end_date_str else None
        
        if car['etat'] == 0:
            car['status'] = 'available'
            car['status_message'] = "Available"
            car['status_color'] = "text-success"
        elif start_date and today < start_date:
            car['status'] = 'available_until'
            car['status_message'] = f"Available on {start_date.strftime('%Y-%m-%d')}"
            car['status_color'] = "text-gray"
        elif end_date and today > end_date and car['etat'] != 0:
            car['status'] = 'not_returned'
            car['status_message'] = "Not returned yet"
            car['status_color'] = "text-danger"
        elif start_date and end_date and start_date <= today <= end_date:
            car['status'] = 'rented'
            car['status_message'] = f"Rented until {end_date.strftime('%Y-%m-%d')}"
            car['status_color'] = "text-warning"
    return render_template('listing.html', cars=cars)

@app.route('/main')
def main():
    return render_template('main.html')

@app.route('/single')
def single():
    return render_template('single.html')


@app.route('/testi', methods=['POST', 'GET'])
def testi():
    # Check if tenant is logged in by verifying the presence of tenant_id in the session
    if 'tenant_id' not in session:
        return redirect(url_for('enter'))  # Redirect to the login page if not logged in

    if request.method == 'POST':
        # Get the comment from the form
        comment = request.form.get('comment')

        if not comment:
            return render_template('testimonials.html', tenant=session, error_message="Please enter a comment.")

        # Get tenant_id and username from session
        tenant_id = session['tenant_id']
        username = session['username']

        # Insert the testimonial into the database
        add_testimonial(tenant_id, username, comment)

        # Redirect to the same page with a success message
        return redirect(url_for('testimonials'))

    # Handle GET request to display the form and any messages
    # Fetch all testimonials from the database to display on the page
    testimonials_list = testimonials_collection.find()

    return render_template('testi.html', tenant=session, testimonials=testimonials_list)

@app.route('/testimonials', methods=['POST', 'GET'])
def testimonials():
    # Check if tenant is logged in by verifying the presence of tenant_id in the session
    if 'tenant_id' not in session:
        return redirect(url_for('enter'))  # Redirect to the login page if not logged in

    if request.method == 'POST':
        # Get the comment from the form
        comment = request.form.get('comment')

        if not comment:
            return render_template('testimonials.html', tenant=session, error_message="Please enter a comment.")

        # Get tenant_id and username from session
        tenant_id = session['tenant_id']
        username = session['username']

        # Insert the testimonial into the database
        add_testimonial(tenant_id, username, comment)

        # Redirect to the same page with a success message
        return redirect(url_for('testimonials'))

    # Handle GET request to display the form and any messages
    # Fetch all testimonials from the database to display on the page
    testimonials_list = testimonials_collection.find()

    return render_template('testimonials.html', tenant=session, testimonials=testimonials_list)



@app.route('/managecar')
def managecar():
    # Check if tenant is logged in by verifying the presence of tenant_id in the session
    if 'tenant_id' not in session:
        return redirect(url_for('enter'))  # Redirect to the login page if not logged in
     # Fetch cars data
    cars = list(cars_collection.find())
    today = datetime.now()
     # Process car data for status and display information
    for car in cars:
        start_date_str = car.get('start_date')  # Using .get() to avoid KeyError
        end_date_str = car.get('end_date')

        # Convert dates to datetime objects if present
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d') if start_date_str else None
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d') if end_date_str else None
    return render_template('managecar.html', tenant=session, cars=cars,  success_message=request.args.get('success_message'))

@app.route('/users')
def users():
    return render_template('users.html', tenant=session)
# auth
@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()  # Clears the session
    return redirect(url_for('enter'))  # Redirect to the login page


@app.route('/dashboard')
def dashboard():
    # Check if tenant is logged in by verifying the presence of tenant_id in the session
    if 'tenant_id' not in session:
        return redirect(url_for('enter'))  # Redirect to the login page if not logged in

    # Retrieve only cars with etat = 0 (available cars) from the database
    available_cars = list(cars_collection.find({'etat': 0}))
    for car in available_cars:
        car['_id'] = str(car['_id'])  # Convert ObjectId to string for JSON serialization

    # Pass available cars and tenant info (from session) to the template
    return render_template('dashboard.html', cars=available_cars, tenant=session)

# Function to add a tenant
@app.route('/add_tenant', methods=['POST'])
def add_tenant():
    username = request.form.get('username')
    p = request.form.get('p')
    role = request.form.get('role', 'tenant')  # Default role is 'tenant'
    
    if not username or not p:
        return jsonify({'message': 'Username and password are required!'}), 400

    tenant = {
        'username': username,
        'p': p,
        'role': role,
        'rented_cars': []  # Initialize an empty list for rented cars
    }
    
    # Insert tenant into the tenants collection
    tenants_collection.insert_one(tenant)
    
    return jsonify({'message': 'Tenant added successfully!'}), 201

@app.route('/enter', methods=['GET', 'POST'])
def enter():
    if request.method == 'GET':
        return render_template('enter.html')

    # POST request to verify username and password
    username = request.form.get('username')
    p = request.form.get('p')

    # Find user in the database (tenant or admin)
    user = tenants_collection.find_one({'username': username, 'p': p})

    if user:
        # If the user exists, store the user's ID and role in the session
        session['tenant_id'] = str(user['_id'])  # Store user ID in session
        session['username'] = user['username']  # Optional: store username
        session['role'] = user.get('role', 'tenant')  # Default role is 'tenant'

        # Redirect based on role
        if session['role'] == 'admin':
            return jsonify({'success': True, 'redirect_url': url_for('admindash')}), 200
        else:
            return jsonify({'success': True, 'redirect_url': url_for('dashboard')}), 200
    else:
        # If credentials are incorrect
        return jsonify({'success': False, 'message': 'Invalid username or password!'}), 401

# end auth
@app.route('/add_car', methods=['POST'])
def add_car_route():
    num_imma = request.form.get('num_imma')
    marque = request.form.get('marque')
    modele = request.form.get('modele')
    kilometrage = request.form.get('kilometrage')
    prix_location = request.form.get('prix_location')

    # Handling images
    images = []
    image_files = request.files.getlist('images')
    for img in image_files:
        # Read image binary data and encode it in base64
        encoded_image = base64.b64encode(img.read()).decode('utf-8')
        images.append(encoded_image)

    # Add car to database
    add_car(num_imma, marque, modele, kilometrage, 0, prix_location, images)

    # Set session flag indicating car was successfully added
    session['car_added'] = True

    # Return the car details as part of the response
    return jsonify({
        "message": "Car added successfully!",
        "car": {
            "num_imma": num_imma,
            "marque": marque,
            "modele": modele,
            "kilometrage": kilometrage,
            "prix_location": prix_location,
            "images": images
        }
    }), 200

@app.route('/admindash')
def admindash():
    if 'tenant_id' not in session:
        return redirect(url_for('enter'))  # Redirect to the login page if not logged in

 # Fetch cars data
    cars = list(cars_collection.find())
    today = datetime.now()

    # Process car data for status and display information
    for car in cars:
        start_date_str = car.get('start_date')  # Using .get() to avoid KeyError
        end_date_str = car.get('end_date')

        # Convert dates to datetime objects if present
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d') if start_date_str else None
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d') if end_date_str else None

        # Set car status based on dates and state
        if car['etat'] == 0:
            car['status'] = 'available'
            car['status_message'] = "Available"
            car['status_color'] = "text-success"
        elif start_date and today < start_date:
            car['status'] = 'available_until'
            car['status_message'] = f"Available on {start_date.strftime('%Y-%m-%d')}"
            car['status_color'] = "text-gray"
        elif end_date and today > end_date and car['etat'] != 0:
            car['status'] = 'not_returned'
            car['status_message'] = "Not returned yet"
            car['status_color'] = "text-danger"
        elif start_date and end_date and start_date <= today <= end_date:
            car['status'] = 'rented'
            car['status_message'] = f"Rented until {end_date.strftime('%Y-%m-%d')}"
            car['status_color'] = "text-warning"

    # Fetch testimonials from the database
    testimonials = list(testimonials_collection.find())
    return render_template('admindash.html', tenant=session, cars=cars)

@app.route('/admintestimonials/manage/<action>/<testimonial_id>', methods=['POST'])
def manage_testimonial(action, testimonial_id):
    print(f"Received testimonial_id: {testimonial_id}")  # Temporary debug print

    # Ensure the user is an admin
    if 'tenant_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('enter'))  # Redirect if not logged in as admin

    try:
        # Convert testimonial_id to ObjectId
        testimonial_id = ObjectId(testimonial_id)
    except Exception as e:
        print(f"Error converting testimonial_id to ObjectId: {e}")
        return "Invalid Testimonial ID", 400  # Invalid ObjectId format

    # Fetch the testimonial from the database
    testimonial = testimonials_collection.find_one({'_id': testimonial_id})

    if not testimonial:
        print(f"Testimonial with ID {testimonial_id} not found.")
        return "Testimonial not found", 404  # If no testimonial is found

    if action == 'approve':
        # Approve the testimonial (set 'etat' to 1)
        testimonials_collection.update_one(
            {'_id': testimonial['_id']},
            {'$set': {'etat': 1}}
        )
        return redirect(url_for('admintestimonials'))  # Redirect back to the admin testimonials page

    elif action == 'delete':
        # Delete the testimonial
        testimonials_collection.delete_one({'_id': testimonial['_id']})
        return redirect(url_for('admintestimonials'))  # Redirect back to the admin testimonials page

    return "Method Not Allowed", 405  # If the action isn't approve or delete


@app.route('/admincontact')
def admincontact():
    # Check if tenant is logged in by verifying the presence of tenant_id in the session
    if 'tenant_id' not in session:
        return redirect(url_for('enter'))  # Redirect to the login page if not logged in

    # Fetch all contact messages from the database
    contact_messages = contact_us_collection.find()

    # Render the template and pass the contact messages to it
    return render_template('admincontact.html', tenant=session, contact_messages=contact_messages)

@app.route('/admintestimonials', methods=['POST', 'GET'])
def admintestimonials():
    # Check if tenant is logged in by verifying the presence of tenant_id in the session
    if 'tenant_id' not in session:
        return redirect(url_for('enter'))  # Redirect to the login page if not logged in

    if request.method == 'POST':
        # Get the comment from the form
        comment = request.form.get('comment')

        if not comment:
            return render_template('admintestimonials.html', tenant=session, error_message="Please enter a comment.")

        # Get tenant_id and username from session
        tenant_id = session['tenant_id']
        username = session['username']

        # Insert the testimonial into the database
        add_testimonial(tenant_id, username, comment)

        # Redirect to the same page with a success message
        return redirect(url_for('admintestimonials'))

    # Handle GET request to display the form and any messages
    # Fetch all testimonials from the database to display on the page
    testimonials_list = testimonials_collection.find()

    return render_template('admintestimonials.html', tenant=session, testimonials=testimonials_list)

@app.route('/delete_car/<string:num_imma>', methods=['DELETE'])
def delete_car(num_imma):
    try:
        result = cars_collection.delete_one({"num_imma": num_imma})  # Ensure you are matching by num_imma
        if result.deleted_count > 0:
            return jsonify({"message": "Car deleted successfully!"}), 200
        else:
            return jsonify({"message": "Car not found!"}), 404
    except Exception as e:
        return jsonify({"message": "Error deleting car", "error": str(e)}), 500


@app.route('/update_car/<string:num_imma>', methods=['PUT'])
def update_car(num_imma):
    data = request.get_json()
    
    # Get current car data to retain any unchanged fields like images
    car = cars_collection.find_one({"num_imma": num_imma})
    if not car:
        return jsonify({"message": "Car not found!"}), 404

    # Check for updated data and retain old data if not provided
    updated_data = {
        "marque": data.get('marque', car.get('marque')),
        "modele": data.get('modele', car.get('modele')),
        "kilometrage": data.get('kilometrage', car.get('kilometrage')),
        "prix_location": data.get('prix_location', car.get('prix_location')),
        "images": data.get('images', car.get('images'))  # Retain old images if not updated
    }
    
    # Update the car in the database
    result = cars_collection.update_one({"num_imma": num_imma}, {"$set": updated_data})

    if result.modified_count > 0:
        return jsonify({"message": "Car updated successfully!"}), 200
    else:
        return jsonify({"message": "No changes made."}), 200

@app.route('/get_car/<string:num_imma>', methods=['GET'])
def get_car(num_imma):
    car = cars_collection.find_one({"num_imma": num_imma})
    if car:
        # Remove '_id' from the returned car to avoid returning MongoDB's internal ID field
        car["_id"] = str(car["_id"])
        
        # Ensure images are correctly formatted
        car["images"] = [f"data:image/jpeg;base64,{img}" for img in car.get("images", [])]
        
        return jsonify(car), 200
    else:
        return jsonify({"message": "Car not found!"}), 404



@app.route('/get_all_cars')
def get_all_cars():
    cars = list(cars_collection.find())  # Assuming this fetches all cars
    for car in cars:
        car['_id'] = str(car['_id'])  # Convert ObjectId to string for JSON serialization
        if 'tenant' in car and car['tenant']:  # Check if 'tenant' exists and is not None
            car['tenant'] = {
                'username': car['tenant']['username'],
                'start_date': car['start_date'],
                'end_date': car['end_date']
            }
        else:
            car['tenant'] = None  # Set tenant to None if the car is not rented
    return jsonify(cars)

@app.route('/rent_car/<car_id>', methods=['PUT'])
def rent_car_route(car_id):
    try:
        # Parse request data
        data = request.json
        tenant = {
            "_id": data['_id'],
            "username": data['username']
        }
        start_date = data.get('start_date', str(datetime.now().date()))
        end_date = data['end_date']

        # Attempt to rent the car
        rental_success = rent_car(car_id, tenant, start_date, end_date)

        if rental_success:
            # Send success response and exit
            return jsonify({"message": "Car rented successfully!"}), 200

        # Send error response for car not available or not found
        return jsonify({"error": "Car not available or not found"}), 404

    except Exception as e:
        # Handle unexpected errors
        print(f"Error: {e}")
        return jsonify({"error": "Something went wrong. Please try again."}), 500

@app.route('/mycars', methods=['GET'])
def my_cars():
    try:
        tenant_id = request.args.get('tenant_id')  # Get tenant_id from query parameter
        if not tenant_id:
            return jsonify({"error": "Tenant not logged in"}), 401  # Return an error if no tenant_id

        # Find cars that have the matching tenant_id in the 'tenant._id' field
        rented_cars = cars_collection.find({"tenant._id": tenant_id})

        # If cars are found, return them
        cars_list = []
        for car in rented_cars:
            car_data = {
                "num_imma": car.get("num_imma"),
                "marque": car.get("marque"),
                "modele": car.get("modele"),
                "kilometrage": car.get("kilometrage"),
                "etat": car.get("etat"),
                "prix_location": car.get("prix_location"),
                "start_date": car.get("start_date"),
                "end_date": car.get("end_date"),
                "images": car.get("images", [])  # Add the images field
            }
            cars_list.append(car_data)

        if cars_list:
            return jsonify({"rented_cars": cars_list})
        else:
            return jsonify({"message": "No rented cars found for this tenant"}), 404

    except Exception as e:
        print(f"Error: {e}")  # Log any error
        return jsonify({"error": "Something went wrong. Please try again."}), 500


@app.route('/rented_cars/<int:tenant_id>', methods=['GET'])
def rented_cars_route(tenant_id):
    """
    Route to get all cars rented by a specific tenant.
    """
    try:
        print(f"Querying rented cars for tenant_id: {tenant_id}")  # Debug log
        rented_cars = get_rented_cars_by_tenant(tenant_id)
        if rented_cars:
            return jsonify(rented_cars)
        else:
            return jsonify({"message": "No rented cars found for this tenant."}), 404
    except Exception as e:
        print(f"Error occurred while fetching rented cars for tenant_id {tenant_id}: {str(e)}")  # Log the error
        return jsonify({"error": "Internal server error", "details": str(e)}), 500  # Provide error details


@app.route('/renters_with_cars', methods=['GET'])
def renters_with_cars_route():
    """
    Returns a list of renters along with the cars (num_imma) they have rented.
    """
    renters = get_renters_with_rented_cars()
    if renters:
        return jsonify(renters)
    return jsonify({"message": "No renters with cars found."}), 404

@app.route('/non_rented_cars', methods=['GET'])
def non_rented_cars_route():
    """
    Returns a list of non-rented cars (available for rent).
    """
    try:
        # Query MongoDB directly
        non_rented_cars = cars_collection.find({"etat": 0})  # Cars that are available
        cars_list = list(non_rented_cars)  # Convert cursor to list

        if cars_list:
            for car in cars_list:
                car['_id'] = str(car['_id'])  # Convert ObjectId to string for JSON serialization
            return jsonify(cars_list)  # Return the list of non-rented cars
        else:
            return jsonify({"message": "No cars are available for rent."}), 404
    except Exception as e:
        print(f"Error: {e}")  # Log the error to the terminal
        return jsonify({"error": "An unexpected error occurred."}), 500

@app.route('/return_car/<car_num_imma>', methods=['PUT'])
def return_car_route(car_num_imma):
    """
    Route to return a rented car and set it as available.
    """
    car = cars_collection.find_one({"num_imma": car_num_imma})
    if car and car['etat'] == 1:  # Check if car is rented (etat == 1 means rented)
        start_date = car['start_date']
        end_date = car['end_date']
        
        # Calculate the number of days the car was rented
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
        
        rented_days = (end_date_obj - start_date_obj).days
        rental_fees = rented_days * car['prix_location']

        # Calculate if the car was returned late
        extra_fee = 0
        if datetime.now() > end_date_obj:
            late_days = (datetime.now() - end_date_obj).days
            rental_fees += late_days * car['prix_location'] * 2  # Extra late fee
            extra_fee = late_days * car['prix_location'] * 2

        # Update the car's status in the database
        update_result = cars_collection.update_one(
            {"num_imma": car_num_imma},
            {"$set": {
                "etat": 0,  # Set car as available
                "tenant": {},  # Clear tenant info
                "start_date": None,  # Reset start date
                "end_date": None,  # Reset end date
                "total": car.get('total', 0) + rental_fees  # Update total rental cost
            }}
        )

        if update_result.modified_count > 0:
            return jsonify({
                "message": f"Car returned successfully! Rental fees: ${rental_fees:.2f}. Extra fee: ${extra_fee:.2f} for {late_days} late days. Total updated: ${car['total'] + rental_fees:.2f}."
            })
        else:
            return jsonify({"error": "Failed to update car information."}), 500
    return jsonify({"error": "Car not found or not rented."}), 404


@app.route('/return_my_car/<car_num_imma>', methods=['PUT'])
def return_my_car(car_num_imma):
    current_date = datetime.now()
    car = cars_collection.find_one({"num_imma": car_num_imma})
    
    if car and car['etat'] == 1:  # Check if car is rented
        start_date = datetime.strptime(car['start_date'], '%Y-%m-%d')
        end_date = datetime.strptime(car['end_date'], '%Y-%m-%d')
        
        rented_days = (current_date - start_date).days
        rental_fees = rented_days * car['prix_location']
        extra_fee = 0

        if current_date > end_date:
            late_days = (current_date - end_date).days
            rental_fees += late_days * car['prix_location'] * 2  # Extra charge for late return
            extra_fee = late_days * car['prix_location'] * 2

        # Convert total to float to ensure correct addition
        total_amount = float(car['total']) + rental_fees  # Ensure total is a float

        # Update the car in the database with the new total cost and other necessary fields
        update_result = cars_collection.update_one(
            {"num_imma": car_num_imma},
            {"$set": {
                "etat": 0,  # Set car as available
                "tenant": {},  # Clear tenant info
                "start_date": None,  # Reset start date
                "end_date": None,  # Reset end date
                "total": total_amount  # Update the total cost in the database
            }}
        )

        # Check if the update was successful
        if update_result.modified_count > 0:
            return jsonify({
                "message": f"Car returned successfully! Total rental fees: ${rental_fees:.2f}. Extra fee: ${extra_fee:.2f} for {late_days} late days. Updated total: ${total_amount:.2f}."
            })
        else:
            return jsonify({"error": "Failed to update car information."}), 500

    return jsonify({"error": "Car not found or not rented."}), 404


# list of all tenants
@app.route('/get_all_tenants', methods=['GET'])
def get_all_tenants():
    try:
        # Fetch all tenants with role='tenant' from the tenants collection
        tenants = tenants_collection.find({"role": "tenant"})

        # Convert the MongoDB cursor to a list of dictionaries
        tenants_list = []
        for tenant in tenants:
            tenant_data = {
                'id': str(tenant['_id']),  # Convert '_id' to string
                'username': tenant['username'],
                'role': tenant['role'],
                'rented_cars': tenant.get('rented_cars', [])  # Get rented_cars if present, default to empty list
            }
            tenants_list.append(tenant_data)

        # Return the list of tenants as a JSON response
        return jsonify(tenants_list), 200

    except Exception as e:
        print(f"Error: {e}")  # Log any error
        return jsonify({"error": "Something went wrong. Please try again."}), 500

@app.route('/contact_us', methods=['POST', 'GET'])
def add_contact_us():
    if request.method == 'POST':
        # Get form data
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        message = request.form.get('message')

        if not all([first_name, last_name, email, message]):
            return render_template('contact.html', error_message="All fields are required.")

        # Insert data into MongoDB
        add_contact(first_name, last_name, email, message)

        # Redirect to the same page and pass a success message
        return redirect(url_for('add_contact_us', success_message="Thank you for your message!"))

    # Handle GET request to display the form and success message
    return render_template('contact.html')


if __name__ == '__main__':
    app.run(debug=True)