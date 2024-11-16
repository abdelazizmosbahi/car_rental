from datetime import datetime
from flask import Flask, request, jsonify
from models import add_car, get_renters_with_rented_cars, get_rented_cars_by_tenant, delete_car, update_car, get_car_by_id, get_all_cars, rent_car

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
    rented_cars = get_rented_cars_by_tenant(tenant_id)
    if rented_cars:
        return jsonify(rented_cars)
    return jsonify({"message": "No rented cars found for this tenant."}), 404

@app.route('/renters_with_cars', methods=['GET'])
def renters_with_cars_route():
    """
    Returns a list of renters along with the cars (num_imma) they have rented.
    """
    renters = get_renters_with_rented_cars()
    if renters:
        return jsonify(renters)
    return jsonify({"message": "No renters with cars found."}), 404
