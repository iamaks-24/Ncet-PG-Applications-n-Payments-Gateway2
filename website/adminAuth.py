from flask import Blueprint,render_template,Flask,request,jsonify
from pymongo import MongoClient
from .db import admins_collection
from werkzeug.security import generate_password_hash
import uuid

adminAuth=Blueprint('adminAuth',__name__)

@adminAuth.route('/admin_signin',methods=['GET','POST'])
def admin_signin():
    return

@adminAuth.route('/admin_signup',methods=['POST'])
def admin_signup():
    data=request.json

    # validate input
    email=data.get('email')
    password=data.get('password')

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400
    
    # Check if email already exists in the admins collection
    if admins_collection.find_one({"email": email}):
        return jsonify({"error": "Admin with this email already exists"}), 400
    
    # Hash the password
    hashed_password = generate_password_hash(password)

    new_admin={
        "email":email,
        "password":hashed_password,
        "verified":False,
        "verification_token":None #no token until login
    }

    admins_collection.insert_one(new_admin)

    return jsonify({"message": "Admin registered successfully, please log in to verify"}), 201

# @adminAuth.route('/admin_signin',methods=['POST'])
# def admin_signin():
#     if request.method=="POST":
#         data=request.json
