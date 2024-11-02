from flask import Blueprint,render_template,Flask,request,jsonify,url_for,flash,session,redirect
from pymongo import MongoClient
from .db import admins_collection
from werkzeug.security import generate_password_hash,check_password_hash
from flask_mail import Mail,Message
import random,time
mail=Mail()

adminAuth=Blueprint('adminAuth',__name__)

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

@adminAuth.route('/admin_signin',methods=['GET','POST'])
def admin_signin():
    if request.method=="POST":
        email=request.form.get('email')
        password=request.form.get('password')

        if not email or not password:
                flash('Email and password are required', category='error')
                return redirect(url_for('adminAuth.admin_signin'))
        
        admin=admins_collection.find_one({"email":email})
        if not admin or not check_password_hash(admin['password'],password):
            flash('You are not authorized to view admin panel',category='error')
            return redirect(url_for('adminAuth.admin_signin'))
        
        otp=random.randint(100000,999999)
        session['otp']=otp
        session['email']=email
        session['otp_timestamp']=time.time()

        msg = Message('Admin Login OTP Verification', recipients=[email])
        msg.body = f"Hello,\nYour OTP for login is {otp}. It is valid for 5 minutes."
        try:
            mail.send(msg)
            flash('OTP sent to your email', category='info')
        except Exception as e:
            print(f"Error sending email: {e}")
            flash('Error sending email. Please try again.', category='error')
            return redirect(url_for('adminAuth.admin_signin'))

        return redirect(url_for('adminAuth.verify_otp'))

    return render_template('admin_signin.html')

@adminAuth.route('/verify_otp',methods=['GET','POST'])
def verify_otp():
    if request.method=='POST':
        otp_entered=request.form.get('otp')
        email=session.get('email')
        otp_session=session.get('otp')
        otp_timestamp=session.get('otp_timestamp')

        if not email or not otp_session:
            flash('Session expired. Please log in again.', category='error')
            return redirect(url_for('adminAuth.admin_signin'))

        if str(otp_session)==str(otp_entered) and time.time()-otp_timestamp<300:
            session.pop('otp')  # Clear OTP from session
            session['otp_verified'] = True
            flash('Login successful', category='success')
            return redirect(url_for('admin_panel.admin_dashboard'))  # Redirect to dashboard or desired page
        else:
            flash('Invalid or expired OTP', category='error')
            return redirect(url_for('adminAuth.verify_otp'))
    return render_template('Admin_otp_verify.html')

