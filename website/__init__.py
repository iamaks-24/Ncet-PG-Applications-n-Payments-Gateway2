from flask import Flask
from flask_mail import Mail


mail=Mail()

def create_app():
    app=Flask(__name__)
    app.config['SECRET_KEY']='Ncet_Application_Form(Payments)'
   

    # configuartion send mail
    app.config["MAIL_SERVER"]='smtp.gmail.com'
    app.config["MAIL_PORT"]=587
    app.config["MAIL_USERNAME"]='afreen04.taj.s@gmail.com'
    app.config['MAIL_PASSWORD']='kymeppuahofbspbj'
    app.config["MAIL_USE_TLS"]=True #enables transport layer security for secure email communication
    app.config["MAIL_USE_SSL"]=False
    app.config['MAIL_DEFAULT_SENDER']='afreen04.taj.s@gmail.com'
    # mail=Mail(auth)#Mail is class of flask-mail
    mail.init_app(app)#initializes email configuration

    from .app_form import app_form
    from .auth import auth
    from .adminAuth import adminAuth
    from .programs import programs
    from .admin_panel import admin_panel

    app.register_blueprint(app_form,url_prefix='/')
    app.register_blueprint(auth,url_prefix='/')
    app.register_blueprint(adminAuth,url_prefix='/')
    app.register_blueprint(programs,url_prefix='/')
    app.register_blueprint(admin_panel,url_prefix='/')

    return app
