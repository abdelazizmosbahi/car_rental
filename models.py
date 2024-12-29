from pymongo import MongoClient
from datetime import datetime

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['car_rental_db']  # The database for the car rental app
cars_collection = db['voitures']
contact_us_collection = db.contact_us  # Collection for contact us messages
testimonials_collection = db.testimonials  # Collection for contact us messages
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
        "total": 0 , # Initialize the total field to 0
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


def rent_car(car_id, tenant, start_date, end_date):
    # Convert string dates to datetime objects for comparison
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')

    # Find the car by its 'num_imma'
    car = cars_collection.find_one({"num_imma": car_id})
    
    if car:
        # Check if the car is already rented for overlapping periods
        existing_rentals = cars_collection.find({"num_imma": car_id, "etat": 1})  # Rented cars
        for rental in existing_rentals:
            # Convert the start and end dates of the existing rental
            existing_start_date = datetime.strptime(rental['start_date'], '%Y-%m-%d')
            existing_end_date = datetime.strptime(rental['end_date'], '%Y-%m-%d')

            # Check if there is any overlap with existing rental
            if (start_date < existing_end_date and end_date > existing_start_date):
                return False  # Overlap found, cannot rent the car

        # If the car is planned for future rental (before today)
        if start_date > datetime.now():
            # The car is still available (but planned for future rental), keep etat 0
            car['tenant'] = tenant
            car['start_date'] = start_date.strftime('%Y-%m-%d')
            car['end_date'] = end_date.strftime('%Y-%m-%d')
            car['etat'] = 0  # Keep the car available (etat = 0)
        else:
            # Rent the car if it's available
            car['tenant'] = tenant
            car['start_date'] = start_date.strftime('%Y-%m-%d')
            car['end_date'] = end_date.strftime('%Y-%m-%d')
            car['etat'] = 1  # Mark the car as rented
        
        # Update the car document in the cars collection
        cars_collection.update_one({"num_imma": car_id}, {"$set": car})

        # Add the marque of the rented car to the tenant's record
        tenant_collection.update_one(
            {"_id": tenant["_id"]},  # Find the tenant by their unique ID
            {"$push": {"rented_cars": {"marque": car['marque']}}}  # Add the marque to rented_cars
        )
        return True
    return False





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

# Function to add contact us message to the database
def add_contact(first_name, last_name, email, message):
    contact_us_data = {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "message": message
    }
    contact_us_collection.insert_one(contact_us_data)

# Function to add a testimonial to the database
def add_testimonial(tenant_id, username, comment):
    testimonial_data = {
        "tenant_id": tenant_id,
        "username": username,
        "comment": comment,
        "etat": 0  # Default status is 'unapproved'
    }
    testimonials_collection.insert_one(testimonial_data)
