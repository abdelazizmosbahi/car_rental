from pymongo import MongoClient
from datetime import datetime

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['car_rental_db']  # The database for the car rental app
cars_collection = db['voitures']

# Cars collection
cars_collection = db['voitures']
tenant_collection = db['tenant']  # The tenant collection

# Directly test the MongoDB query
non_rented_cars = cars_collection.find({"etat": 0})
print(list(non_rented_cars))  # Print the results of the query

# Function to add a car
def add_car(num_imma, marque, modele, kilometrage, etat, prix_location, images):
    """
    Adds a car to the database.
    `images` is expected to be a list of image URLs.
    """
    car = {
        "num_imma": num_imma,
        "marque": marque,
        "modele": modele,
        "kilometrage": kilometrage,
        "etat": etat,  # 0: available, 1: rented
        "prix_location": prix_location,
        "tenant": None,  # No tenant when the car is available
        "images": images  # List of image URLs
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


# Rent a car function
def rent_car(num_imma, tenant, start_date, end_date):
    """
    Updates a car's state to 'rented' and adds tenant information along with the rental period.
    """
    rental_info = {
        "tenant": tenant,
        "start_date": start_date,
        "end_date": end_date
    }

    print(f"Attempting to rent car with num_imma: {num_imma} and rental info: {rental_info}")  # Debug print

    result = cars_collection.update_one(
        {"num_imma": num_imma, "etat": 0},  # Ensure the car is available
        {"$set": {"etat": 1, **rental_info}}
    )

    if result.matched_count > 0:
        print("Car rented successfully!")  # Debug print
        return True
    else:
        print("Car not available or not found.")  # Debug print
        return False
def get_rented_cars_by_tenant(tenant_id):
    """
    Retrieves all cars rented by a specific tenant based on tenant's id_loc.
    """
    try:
        print(f"Querying rented cars for tenant_id: {tenant_id}")  # Log the tenant_id for debugging
        query = {"tenant.id_loc": tenant_id, "etat": 1}  # Ensure we're looking for rented cars (etat: 1)
        print(f"MongoDB Query: {query}")  # Log the query

        rented_cars_cursor = cars_collection.find(query)
        rented_cars_list = list(rented_cars_cursor)  # Convert cursor to list

        if rented_cars_list:
            # Convert ObjectId to string for JSON serialization
            for car in rented_cars_list:
                car['_id'] = str(car['_id'])  # Convert ObjectId to string
                # If there are any nested ObjectIds, convert them to strings as well
                if 'tenant' in car:
                    car['tenant']['_id'] = str(car['tenant'].get('_id', ''))  # Convert tenant's _id if present
            print(f"Found {len(rented_cars_list)} rented car(s) for tenant_id: {tenant_id}")
            return rented_cars_list
        else:
            print("No cars found for this tenant.")
            return []
    except Exception as e:
        print(f"Error occurred while fetching rented cars for tenant_id {tenant_id}: {str(e)}")
        return {"error": "Internal server error", "details": str(e)}  # Return error details


def get_non_rented_cars():
    non_rented_cars = cars_collection.find({"etat": 0})  # Cars that are available
    return list(non_rented_cars)  # Convert the cursor to a list for easy handling


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
    non_rented_cars = cars_collection.find({"etat": 0})  # Cars that are available
    return list(non_rented_cars)  # Convert the cursor to a list for easy handling
