from flask import Blueprint, render_template, request,redirect,url_for,flash,session,jsonify
from werkzeug.security import generate_password_hash,check_password_hash
import re
from .db import MBA_users_collection,MCA_users_collection,counters_collection,temp_users_collection
from functools import wraps
from flask_mail import *
from flask_mail import Mail
import random
import time
mail=Mail()
auth=Blueprint('auth',__name__)

@auth.route('/')
def LandingPage():
    session['signin']=False
    return render_template('LandingPage.html')


# route protection decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args,**kwargs):
        if 'user' not in session:
            flash('You need to signin first.','error')
            return redirect(url_for('auth.signin'))
        return f(*args,**kwargs)#otherwise,allow access to the route
    return decorated_function

def generate_application_number(program):
    if program not in ['MBA','MCA']:
        raise ValueError("Invalid program. Must be 'MBA' or 'MCA'.")
    
    # select the correct counter ID based on the program
    counter_id=f"{program}_application_number"

    counter=counters_collection.find_one_and_update(
        {"_id":counter_id},
        {"$inc":{"sequence_value":1}},
        return_document=True
        )
    sequence_number=counter["sequence_value"]
    app_number=f"NDC25{program}{sequence_number:03d}"
    return app_number


@auth.route('/resend_otp', methods=['GET', 'POST'])
def resend_otp():
    email = session.get('email')
    otp_resend_count = session.get('otp_resend_count', 0)
    otp_timestamp = session.get('otp_timestamp')

    if not email:
        flash('Invalid request. Please try again.', category='error')
        return redirect(url_for('auth.signup'))

    if otp_resend_count >= 3:
        flash('You have exceeded the OTP resend limit. Please try again later.', category='error')
        return redirect(url_for('auth.signup'))

    # Check if the previous OTP has expired
    current_time = time.time()
    otp_expiration_time = 300  # OTP validity period in seconds (5 minutes)

    if otp_timestamp and (current_time - otp_timestamp) <= otp_expiration_time:
        flash('You can request a new OTP only after the previous OTP expires.', category='error')
        return redirect(url_for('auth.signup'))

    # Render a confirmation template
    return render_template('confirm_resend_otp.html')


@auth.route('/confirm_resend_otp', methods=['POST'])
def confirm_resend_otp():
    email = session.get('email')
    otp_resend_count = session.get('otp_resend_count', 0)
    otp_timestamp = session.get('otp_timestamp')
    
    # Check if the resend is valid
    if not email:
        flash('Invalid request. Please try again.', category='error')
        return redirect(url_for('auth.signup'))

    if otp_resend_count >= 3:
        flash('You have exceeded the OTP resend limit. Please try again later.', category='error')
        return redirect(url_for('auth.signup'))

    # Check if the previous OTP has expired
    current_time = time.time()
    otp_expiration_time = 300  # OTP validity period in seconds (5 minutes)

    if otp_timestamp and (current_time - otp_timestamp) > otp_expiration_time:
        # OTP expired, allow resend
        otp = random.randint(100000, 999999)
        session['otp'] = otp
        session['otp_timestamp'] = current_time
        session['otp_resend_count'] = otp_resend_count + 1

        msg = Message('Ncet PG Application form email verification', sender='afreen04.taj.s@gmail.com', recipients=[email])
        msg.body = f"Hi,\nYour new email OTP is: {otp}"

        try:
            mail.send(msg)
            flash('OTP has been resent. Please check your email.', category='info')
            return redirect(url_for('auth.verify_otp'))
        except Exception as e:
            print(f"Error sending email: {e}")
            flash('Error sending email. Please try again.', category='error')
    else:
        flash('You can request a new OTP only after the previous OTP expires.', category='error')

    return redirect(url_for('auth.signup'))




@auth.route('/verify_otp/', methods=['POST'])
def verify_otp():
    selected_program=request.form.get('program')
    entered_otp = request.form.get('otp')
    email = session.get('email')
    otp = session.get('otp')
    otp_timestamp = session.get('otp_timestamp')
    print(otp_timestamp)
    print(email)
    print(otp)
    print(entered_otp)
    if not email or not otp or not otp_timestamp:
        flash('Invalid request. Please try again.', category='error')
        return redirect(url_for('auth.signup',program=selected_program))
    user=temp_users_collection.find_one({'email':email,'email_verified':False})

    if user:
        current_time = time.time()
        # application_number = user.get('application_number')
        otp_expiration_time = 300  # OTP validity period in seconds (5 minutes)

        if current_time - otp_timestamp > otp_expiration_time:
            flash('OTP has expired. Please request a new one.', category='error')
            return redirect(url_for('auth.signup',program=selected_program))
            
        if entered_otp == str(otp):
        # store users permanently
            app_number=generate_application_number(selected_program)
            session['application_number']=app_number
            if 'MBA' in app_number:
                MBA_users_collection.insert_one(
                {
                    "name":user['name'],
                    "email":user['email'],
                    "password":user['password'],
                    "application_number":app_number,
                    "email_verified":True
                }
                )
            else:
                MCA_users_collection.insert_one(
                {
                    "name":user['name'],
                    "email":user['email'],
                    "password":user['password'],
                    "application_number":app_number,
                    "email_verified":True
                }
                )

            # delete user from temp
            temp_users_collection.delete_one({'email':email})

            flash('Email verified successfully and Application number is generated!Please sign in',category='success')
            try:
                msg = Message('Application Number | NCET-PG Admissions Gateway', sender='afreen04.taj.s@gmail.com', recipients=[email])
                msg.body = f"Your Application number for NCET-PG Admissions Gateway is {app_number}."
                mail.send(msg)
            except Exception as e:
                flash(f'error sending mail! {e}') 
            
            return render_template('app_num_popup.html', app_number=app_number,program=selected_program)
        else:
            flash('Invalid OTP,please try again!',category='error')
            # return redirect(url_for('auth.signup',program=selected_program))
            return render_template('email_verify.html',email=email,program=selected_program)

    flash('Session expired or invalid request.Please sign up again.',category='error')
    return redirect(url_for('auth.signup',program=selected_program))

@auth.route('/signup/',methods=['GET','POST'])
def signup():
    if request.method=='POST':
        selected_program=request.form.get('program')
        name=request.form.get('name')
        email=request.form.get('email')
        password=request.form.get('password')

        # validating email format
        #  [^@]+: This part ensures that the email has one or more characters before the @ symbol, and the ^ inside the brackets ([]) indicates "any character except @".
        # @: This matches the @ symbol, which is mandatory in every email address.

        # [^@]+: This part again ensures that there is at least one character after the @ symbol but before the ..

        # \.: This matches the dot (.) that typically separates the domain name from the top-level domain (e.g., ".com").

        # [^@]+: This part ensures that there is at least one character after the dot.

        if not re.match(r"[^@]+@[^@]+\.[^@]+",email):
            flash('Invalid email address!',category='error')
            return redirect(url_for('auth.signup', program=selected_program))
        
        # check for email already existing in database
        if selected_program=='MBA':
            if MBA_users_collection.find_one({'email':email}):
                flash(f'Email already registered for MBA program!',category='error')
                return redirect(url_for('auth.signup', program=selected_program))
        elif selected_program=='MCA':
            if MCA_users_collection.find_one({'email':email}):
                flash(f'Email already registered for MCA program!',category='error')
                return redirect(url_for('auth.signup', program=selected_program))

        
        # otp send bfr storing to db
        otp=random.randint(100000,999999)
        session['otp']=otp
        session['email']=email
        session['otp_resend_count']=0
        session['otp_timestamp'] = time.time()

        # email verification
        # Message->class

        # subject
        msg=Message('Ncet PG Application form email verification',sender='afreen04.taj.s@gmail.com',recipients=[email])

        # msg body,otp must b string so that it can b written in the body
        msg.body="Hi"+name+"\nYour email OTP is:" +str(otp)

        try:
            mail.send(msg)
        except Exception as e:
            print(f"Error sending email: {e}")
            flash('Error sending email. Please try again.', category='error')
            return redirect(url_for('auth.signup', program=selected_program))


        # temporarily store user to db
        hashed_password=generate_password_hash(password)

        # app_number=generate_application_number()

        # inserting user into the data base
        new_user={
            "name":name,
            "email":email,
            "password":hashed_password,
            "application_number":None,
            "email_verified":False,
            "otp":otp,
            "otp_timestamp":time.time()
        }
        temp_users_collection.insert_one(new_user)
       
        return render_template('email_verify.html',email=email,program=selected_program)

    selected_program=request.args.get('program')
    print(selected_program)
    if selected_program not in ['MBA','MCA']:
        return 'Invalid program selection..........',400
    return render_template('signup.html',program=selected_program)

@auth.route('/reset_password',methods=['GET','POST'])
def reset_password():
    if request.method=='POST':
        selected_program=request.form.get('program')
        new_password=request.form.get('new_password')
        confirm_password=request.form.get('confirm_password')
        email=session.get('email')

        if selected_program=='MBA':
            user=MBA_users_collection.find_one({"email":email})
        elif selected_program=='MBA':
            user=MCA_users_collection.find_one({"email":email})

        current_hashed_password=user['password']

        if check_password_hash(current_hashed_password, new_password):
            flash('New password cannot be the same as the current password. Please choose a different password.', category='error')
            return redirect(url_for('auth.reset_password',program=selected_program))
        
        if new_password != confirm_password:
            flash('Passwords do not match. Please try again.', category='error')
            return redirect(url_for('auth.reset_password',program=selected_program))

        hashed_password=generate_password_hash(new_password)

        if selected_program=='MBA':
            MBA_users_collection.update_one({"email":email},{"$set":{"password":hashed_password}})
        elif selected_program=='MCA':
            MCA_users_collection.update_one({"email":email},{"$set":{"password":hashed_password}})


        session.pop('email',None)

        flash('Your password has been successfully updated. Please log in with your new password.', category='success')
        return redirect(url_for('auth.signin',program=selected_program))
    return render_template('reset_password.html')

# @auth.route('/verify_password_reset_otp',methods=['GET','POST'])
@auth.route('/verify_password_reset_otp',defaults={'program':None},methods=['GET','POST'])
@auth.route('/verify_password_reset_otp/<program>',methods=['GET','POST'])
def verify_password_reset_otp(program):
    if request.method=='POST':
        selected_program=program or request.form.get('program')
        entered_otp=request.form.get('otp')
        email=session.get('email')
        saved_otp=session.get('otp')
        otp_timestamp=session.get('otp_timestamp')
    
        current_time = time.time()
        if otp_timestamp and (current_time - otp_timestamp) > 300:
            flash('OTP has expired. Please request a new one.', category='error')
            return redirect(url_for('auth.forgot_password',program=selected_program))
        
        if int(entered_otp)==saved_otp:
            session.pop('otp', None)
            session.pop('otp_timestamp', None)
            flash('OTP verified. Please set a new password.', category='success')
            return redirect(url_for('auth.reset_password',program=selected_program))
        else:
            flash('Invalid OTP. Please try again.', category='error')
    return render_template('verify_password_reset_otp.html',program=program)

@auth.route('/forgot_password',methods=['GET','POST'])
def forgot_password():
    if request.method=='POST':
        selected_program=request.form.get('program')
        email=request.form.get('email')

        if selected_program=='MBA':
            user=MBA_users_collection.find_one({'email':email})
        elif selected_program=='MCA':
            user=MCA_users_collection.find_one({'email':email})

        if user:
            otp = random.randint(100000, 999999)
            session['otp'] = otp
            session['email'] = email
            session['otp_timestamp'] = time.time()

            try:
                msg = Message('Password Reset OTP', sender='afreen04.taj.s@gmail.com', recipients=[email])
                msg.body = f"Your OTP for password reset is {otp}."
                mail.send(msg)
                flash('OTP has been sent to your email. Please check your inbox.', category='info')
                return redirect(url_for('auth.verify_password_reset_otp',program=selected_program))
            except Exception as e:
                flash(f'error sending mail! {e}') 
        else:
            flash('This email is not registered.', category='error')
    selected_program=request.args.get('program')
    print(selected_program)
    print("check")
    if selected_program not in ['MBA','MCA']:
        return 'Invalid program selection..........',400
    return render_template('forgot_password.html',program=selected_program)


# @auth.route('/verify_application_number_otp',methods=['GET','POST'])
@auth.route('/verify_application_number_otp', defaults={'program': None}, methods=['GET', 'POST'])
@auth.route('/verify_application_number_otp/<program>', methods=['GET', 'POST'])
def verify_application_number_otp(program):
    if request.method=='POST':
        selected_program=program or request.form.get('program')
        entered_otp=request.form.get('otp')
        email=session.get('email')
        saved_otp=session.get('otp')
        otp_timestamp=session.get('otp_timestamp')

        current_time=time.time()
        if otp_timestamp and (current_time-otp_timestamp)>300:
            flash('OTP has expired.Please request a new one.',category='error')
            return redirect(url_for('auth.forgot_application_number'))
        
        if int(entered_otp)==saved_otp:
            if selected_program=='MBA':
                user =MBA_users_collection.find_one({"email":email})
            elif selected_program=='MCA':
                user =MCA_users_collection.find_one({"email":email})
            if user:
                application_number=user.get('application_number')

                session.pop('otp',None)
                session.pop('otp_timestamp',None)

                try:
                    msg=Message('Your Application Number', sender='afreen04.taj.s@gmail.com',recipients=[email])
                    msg.body = f"Hi,\nYour application number is: {application_number}."
                    mail.send(msg)
                    flash('Your application number has been sent to your email.', category='success')
                    return redirect(url_for('auth.signin',program=selected_program))
                except Exception as e:
                    flash(f'Error sending mail! {e}')
                    return redirect(url_for('auth.forgot_application_number',program=selected_program))
            else:
                flash('User not found.',category='error')
                return redirect(url_for('auth.forgot_application_number',program=selected_program))
        else:
            flash('Invalid OTP. Please try again.', category='error')
            return redirect(url_for('auth.verify_application_number_otp',program=selected_program))
    
    return render_template('verify_application_number_otp.html',program=program)

@auth.route('/forgot_application_number',methods=['GET','POST'])
def forgot_application_number():
    if request.method=='POST':
        selected_program=request.form.get('program')
        email=request.form.get('email')
        print(selected_program)
        print(email)
        if selected_program=='MBA':
            user =MBA_users_collection.find_one({"email":email})
        elif selected_program=='MCA':
            user =MCA_users_collection.find_one({"email":email})

        if user:
            otp=random.randint(100000,999999)
            session['otp']=otp
            session['email']=email
            session['otp_timestamp']=time.time()

            try:
                msg=Message('Application Number Retrieval OTP',sender='afreen04.taj.s@gmail.com',recipients=[email])
                msg.body=f"Your OTP for retrieving the application number is {otp}."
                mail.send(msg)
                flash('OTP sent to your email.Please check your inbox.',category='info')
                return redirect(url_for('auth.verify_application_number_otp',program=selected_program))
            except Exception as e:
                flash(f"Error sending mail! {e}")
                return redirect(url_for('auth.forgot_application_number',program=selected_program))
        else:
            flash('This email is not registered.',category='error')
    selected_program=request.args.get('program')
    print(selected_program)
    if selected_program not in ['MBA','MCA']:
        return 'Invalid program selection..........',400
    return render_template('forgot_application_number.html',program=selected_program)
            

@auth.route('/signin',methods=['GET','POST'])
def signin():
    if request.method=='POST':
        selected_program=request.form.get('program')
        app_number=request.form.get('application_number')
        password=request.form.get('password')
        session['signin']=True

        if selected_program=='MBA':
            user=MBA_users_collection.find_one({"application_number":app_number})
        elif selected_program=='MCA':
            user=MCA_users_collection.find_one({"application_number":app_number})


        if user:
            if check_password_hash(user['password'],password):
                # user session
                session['user']=user['name']
                session['application_number']=user['application_number']

                flash(f'Welcome, {user["name"]}!','success')
                return redirect(url_for('auth.home'))
            else:
                flash('Invalid password!','error')
        else:
            flash('Invalid application number!','error')
        
        return redirect(url_for('auth.signin'))#after encountering errors
    selected_program=request.args.get('program')
    print(selected_program)
    if selected_program not in ['MBA','MCA']:
        return 'Invalid program selection..........',400
    return render_template('signin.html',program=selected_program)#get request

@auth.route('/signout')
def signout():
    # clearing session
    session.pop('user',None)
    session.pop('application_number',None)
    

    flash('You have been signed out!','success')
    return redirect(url_for('auth.signin'))

@auth.route('/home')
@login_required
def home():
    if 'user' not in session:
        flash('You need to sign in to access the home page','error')
        return redirect(url_for('auth.signin'))
    
    user_name=session.get('user')
    application_number=session.get('application_number')
    

    if 'progress' not in session:
        session['progress'] = {'page1':False,'page2':False,'page3':False}
    

    return redirect(url_for('app_form.page1'))

    # Pass the completion status to the template
    # return render_template('home.html', completed_steps=session['completed_steps'])

    # return render_template('home.html',user_name=user_name,application_number=application_number)

