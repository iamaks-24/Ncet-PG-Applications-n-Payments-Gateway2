from flask import Blueprint,render_template

adminAuth=Blueprint('adminAuth',__name__)

@adminAuth.route('/admin_signin',methods=['GET','POST'])
def admin_signin():
    return