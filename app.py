from datetime import datetime
from flask import Flask, request, jsonify, render_template
from models import get_all_cars
from models import add_car, cars_collection, return_car, get_renters_with_rented_cars, get_rented_cars_by_tenant,get_non_rented_cars, delete_car, update_car, get_car_by_id, get_all_cars, rent_car


#index html page config
app = Flask(__name__)

@app.route('/')
def index():
    print("Rendering the index page")
    cars = get_all_cars()
    return render_template('index.html', cars=cars)
#index html page config

app = Flask(__name__)

@app.route('/add_car', methods=['POST'])
def add_car_route():
    data = request.json
    add_car(data['num_imma'], data['marque'], data['modele'], data['kilometrage'], data['etat'], data['prix_location'])
    return jsonify({"message": "Car added successfully!"}), 201

@app.route('/delete_car/<int:num_imma>', methods=['DELETE'])
def delete_car_route(num_imma):
    if delete_car(num_imma):
        return jsonify({"message": "Car deleted successfully!"})
    return jsonify({"error": "Car not found"}), 404

@app.route('/update_car/<int:num_imma>', methods=['PUT'])
def update_car_route(num_imma):
    updates = request.json
    if update_car(num_imma, updates):
        return jsonify({"message": "Car updated successfully!"})
    return jsonify({"error": "Car not found"}), 404

@app.route('/get_car/<int:num_imma>', methods=['GET'])
def get_car_by_id_route(num_imma):
    car = get_car_by_id(num_imma)
    if car:
        return jsonify(car)
    return jsonify({"error": "Car not found"}), 404

@app.route('/get_all_cars', methods=['GET'])
def get_all_cars_route():
    cars = get_all_cars()
    return jsonify(cars)

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
    app.run(debug=True)