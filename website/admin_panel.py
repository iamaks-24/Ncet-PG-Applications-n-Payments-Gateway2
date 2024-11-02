from flask import Blueprint,request,render_template,send_file,abort
from bson.objectid import ObjectId
from io import BytesIO
from pymongo import MongoClient
from .db import MBA_users_collection,MCA_users_collection

admin_panel=Blueprint('admin_panel',__name__)

@admin_panel.route('/admin_dashboard')
def admin_dashboard():
    mba_count=MBA_users_collection.count_documents({})
    mca_count=MCA_users_collection.count_documents({})

    return render_template('admin_dashboard.html',mba_count=mba_count,mca_count=mca_count)

@admin_panel.route('/mba_dashboard',methods=['GET'])
def mba_dashboard():
    # Get search query from request arguments
    search_name = request.args.get('name', '').strip()
    search_email = request.args.get('email', '').strip()

    # Build a query dictionary based on search inputs
    query = {}
    if search_name:
        query['name'] = {"$regex": search_name, "$options": "i"}  # Case-insensitive match
    if search_email:
        query['email'] = {"$regex": search_email, "$options": "i"}

    # Fetch matching records from the MBA collection
    mba_data = list(MBA_users_collection.find(query))
    
    return render_template('mba_dashboard.html', data=mba_data)

@admin_panel.route('/mca_dashboard', methods=['GET'])
def mca_dashboard():
    # Get search query from request arguments
    search_name = request.args.get('name', '').strip()
    search_email = request.args.get('email', '').strip()

    # Build a query dictionary based on search inputs
    query = {}
    if search_name:
        query['name'] = {"$regex": search_name, "$options": "i"}  # Case-insensitive match
    if search_email:
        query['email'] = {"$regex": search_email, "$options": "i"}

    # Fetch matching records from the MCA collection
    mca_data = list(MCA_users_collection.find(query))
    
    return render_template('mca_dashboard.html', data=mca_data)

@admin_panel.route('/view_pdf/<program_type>/<user_id>', methods=['GET'])
def view_pdf(program_type, user_id):
    # Determine the collection based on program type
    if program_type == 'MBA':
        user = MBA_users_collection.find_one({"_id": ObjectId(user_id)})
    elif program_type == 'MCA':
        user = MCA_users_collection.find_one({"_id": ObjectId(user_id)})
    else:
        abort(404)  # Invalid program type

    # If no user or no PDF file found, return a 404 error
    if not user or 'pdf_file' not in user:
        abort(404)

    # Convert binary PDF data to a stream
    pdf_data = BytesIO(user['pdf_file'])

    # Serve the PDF file to be viewed in the browser
    return send_file(pdf_data, mimetype='application/pdf', as_attachment=False)
