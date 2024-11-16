from pymongo import MongoClient
from datetime import datetime

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['car_rental_db']  # The database for the car rental app

# Cars collection
cars_collection = db['voitures']

# Function to add a car
def add_car(num_imma, marque, modele, kilometrage, etat, prix_location):
    car = {
        "num_imma": num_imma,
        "marque": marque,
        "modele": modele,
        "kilometrage": kilometrage,
        "etat": etat,  # 0: available, 1: rented
        "prix_location": prix_location,
        "tenant": None  # No tenant when the car is available
    }
    cars_collection.insert_one(car)


# Function to delete a car
def delete_car(num_imma):
    result = cars_collection.delete_one({"num_imma": num_imma})
    return result.deleted_count > 0  # True if deleted, False if not found

# Function to update a car
def update_car(num_imma, updates):
    result = cars_collection.update_one({"num_imma": num_imma}, {"$set": updates})
    return result.matched_count > 0  # True if the car was found and updated

# Function to get a car by ID
def get_car_by_id(num_imma):
    car = cars_collection.find_one({"num_imma": num_imma})
    if car:
        car['_id'] = str(car['_id'])  # Convert ObjectId to string for JSON serialization
    return car

# Function to get all cars
def get_all_cars():
    cars = list(cars_collection.find())
    for car in cars:
        car['_id'] = str(car['_id'])  # Convert ObjectId to string for JSON serialization
    return cars

def rent_car(num_imma, tenant, start_date, end_date):
    """
    Updates a car's state to 'rented' and adds tenant information along with the rental period.
    """
    rental_info = {
        "tenant": tenant,
        "start_date": start_date,
        "end_date": end_date
    }
    result = cars_collection.update_one(
        {"num_imma": num_imma, "etat": 0},  # Ensure the car is available
        {"$set": {"etat": 1, **rental_info}}
    )
    return result.matched_count > 0  # True if the car was found and updated

def return_car(num_imma):
    """
    Updates a car's state to 'available' and removes rental information.
    """
    result = cars_collection.update_one(
        {"num_imma": num_imma, "etat": 1},  # Ensure the car is currently rented
        {"$set": {"etat": 0, "tenant": None, "start_date": None, "end_date": None}}
    )
    return result.matched_count > 0  # True if the car was found and updated

def get_rented_cars_by_tenant(tenant_id):
    """
    Retrieves all cars rented by a specific tenant based on tenant's id_loc.
    """
    rented_cars = cars_collection.find({"tenant.id_loc": tenant_id, "etat": 1})
    return list(rented_cars)  # Convert the cursor to a list for easy handling

def get_renters_with_rented_cars():
    """
    Retrieves a list of renters along with the cars (num_imma) they have rented.
    """
    renters = []
    rented_cars = cars_collection.find({"etat": 1})  # Only cars that are rented
    for car in rented_cars:
        renter = car.get("tenant")
        if renter:
            renter_info = {
                "id_loc": renter["id_loc"],
                "nom": renter["nom"],
                "prenom": renter["prenom"],
                "adresse": renter["adresse"],
                "num_imma": car["num_imma"]  # Car number
            }
            renters.append(renter_info)
    return renters

def get_non_rented_cars():
    """
    Retrieves a list of cars that are not rented.
    """
    non_rented_cars = cars_collection.find({"etat": 0})  # Cars that are available
    return list(non_rented_cars)  # Convert the cursor to a list for easy handling
