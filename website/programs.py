from flask import Blueprint,render_template,request,redirect,url_for

programs=Blueprint('programs',__name__)

@programs.route('/programs_list',methods=['GET'])
def programs_list():
    return render_template('programs_list.html')