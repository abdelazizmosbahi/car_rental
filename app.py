from datetime import datetime
from flask import Flask, request, jsonify, render_template
from models import get_all_cars
from models import add_car, cars_collection, return_car, get_renters_with_rented_cars, get_rented_cars_by_tenant,get_non_rented_cars, delete_car, update_car, get_car_by_id, get_all_cars, rent_car
from flask import request, render_template, redirect, url_for

from pymongo import MongoClient

app = Flask(__name__)

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['car_rental_db']  # The database for the car rental app
cars_collection = db['voitures']

@app.route('/')
def index():
    # Retrieve all cars from the database (or you can filter as needed)
    cars = list(cars_collection.find())
    for car in cars:
        car['_id'] = str(car['_id'])  # Convert ObjectId to string for JSON serialization
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
    return render_template('listing.html')

@app.route('/main')
def main():
    return render_template('main.html')

@app.route('/single')
def single():
    return render_template('single.html')

@app.route('/testimonials')
def testimonials():
    return render_template('testimonials.html')


@app.route('/managecar')
def managecar():
    return render_template('managecar.html')

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
        img.save(f"static/images/{img.filename}")  # Save image to static directory
        images.append(f"images/{img.filename}")   # Store relative path

    add_car(num_imma, marque, modele, kilometrage, 0, prix_location, images)
    
    # Render the same form page with success message
    return render_template('managecar.html', success_message="Car added successfully!")



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
    updated_data = {
        "num_imma": data.get('num_imma'),  # Allow updating num_imma
        "marque": data.get('marque'),
        "modele": data.get('modele'),
        "kilometrage": data.get('kilometrage'),
        "prix_location": data.get('prix_location'),
        "images": data.get('images')
    }
    
    # You might want to ensure that the new `num_imma` is unique
    if cars_collection.find_one({"num_imma": updated_data["num_imma"]}):
        return jsonify({"message": "Car with this registration number already exists!"}), 400

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
        car["_id"] = str(car["_id"])  # Convert ObjectId to string for JSON compatibility
        return jsonify(car), 200
    else:
        return jsonify({"message": "Car not found!"}), 404



@app.route('/get_all_cars', methods=['GET'])
def get_all_cars_route():
    cars = get_all_cars()
    
    # Check if we got the cars, and log the output
    if cars:
        print(f"Fetched {len(cars)} cars")  # Debugging line
        return jsonify(cars)
    else:
        return jsonify({"message": "No cars found."}), 404


@app.route('/rent_car/<int:num_imma>', methods=['PUT'])
def rent_car_route(num_imma):
    data = request.json  # Tenant info and dates
    tenant = {
        "id_loc": data['id_loc'],
        "nom": data['nom'],
        "prenom": data['prenom'],
        "adresse": data['adresse']
    }
    start_date = data.get('start_date', str(datetime.now().date()))  # Default: today
    end_date = data['end_date']

    if rent_car(num_imma, tenant, start_date, end_date):
        return jsonify({"message": "Car rented successfully!"})
    return jsonify({"error": "Car not available or not found"}), 404

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

@app.route('/return_car/<int:num_imma>', methods=['PUT'])
def return_car_route(num_imma):
    """
    Route to return a rented car and set it as available.
    """
    if return_car(num_imma):
        return jsonify({"message": "Car returned successfully and set as available!"})
    return jsonify({"error": "Car not found or not rented."}), 404

if __name__ == '__main__':
    print("Registered Routes:")
    for rule in app.url_map.iter_rules():
        print(rule)
    app.run(debug=True)