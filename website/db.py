from pymongo import MongoClient

def get_db():
    client=MongoClient("mongodb+srv://NCET-PG_Applications_Gateway:NCET-PG_Applications_Gateway@applicationform.ar70l.mongodb.net/?retryWrites=true&w=majority&appName=ApplicationForm")
    db=client["Ncet_ApplicationForm(Payments)"] #db name
    return db

db=get_db()
# collections
MBA_users_collection=db["MBAusers"]#users name of collection
MCA_users_collection=db["MCAusers"]

temp_users_collection=db["temp_users"]
page1_collection=db["page1_collection"]
page2_collection = db["page2_collection"] 
page3_collection=db["page3_collection"]
page4_collection=db["page4_collection"]

admins_collection=db["admins"]

counters_collection=db['counters']
def initialize_app_number_counter():

    # initializing counter for mba program
    if not counters_collection.find_one({"_id":"MBA_application_number"}):
        counters_collection.insert_one({"_id":"MBA_application_number","sequence_value":0})

    # initializing counter for mca program
    if not counters_collection.find_one({"_id":"MCA_application_number"}):
        counters_collection.insert_one({"_id":"MCA_application_number","sequence_value":0})
initialize_app_number_counter()
