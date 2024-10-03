from flask import Blueprint,render_template,request,redirect,url_for,session,flash,make_response
from xhtml2pdf import pisa
from pymongo import MongoClient
# from pymongo.errors import ConnectionError
from .db import page2_collection,page1_collection,page3_collection,page4_collection

# pdf imports
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io
from flask import send_file,jsonify
import json
from bson import ObjectId
import re

app_form=Blueprint('app_form',__name__)

def page1_locked(application_number):
    lock_status=page1_collection.find_one({"application_number":application_number,"locked":True})
    return lock_status is not None

def lock_page1_for_user(application_number,page_name):
    page1_collection.update_one(
        {"application_number":application_number},
         {"$set":{"locked":True}} )

@app_form.route('/page1', methods=['POST', 'GET'])
def page1():
    if 'signin' not in session or not session['signin']:
        return redirect(url_for('auth.signin'))
    
    application_number=session.get("application_number")

    if page1_locked(application_number) and page2_locked(application_number) and page3_locked(application_number) and page4_locked(application_number):
        flash('Application Submitted Successfully','success')
        return redirect(url_for('app_form.preview'))

    if page1_locked(application_number):
        flash('Page1 id already submitted. You cannot edit it anymore.','error')
        return redirect(url_for('app_form.page2'))

    if request.method == 'POST':
        candidate_name = request.form.get('candidateName')
        documents = request.form.getlist('documents')
        other_documents = request.form.get('other_documents')

        form_data = {
            "application_number": session.get('application_number'),
            "candidate_name": candidate_name,
            "other_documents": other_documents,
            "document_status": {
                doc: ("Yes" if doc in documents else "No") for doc in [
                    'Photos',
                    'Aadhar Card',
                    'Marks Cards',
                    'Diploma/Graduation',
                    'Entrance Test Score',
                    'Work Experience',
                    'Other',
                    'Transfer Certificate',
                    'Migration Certificate',
                    'Conduct/Study Certificate',
                    'Caste Certificate',
                    'Income Certificate',
                    'Passport/Visa Copy',
                    'Rank/Score Card',
                    '3 Passport and 3 Stamp size photos',
                    'Copy of Aadhar card',
                    '10th/SSLC and 10+2/PUC marks cards',
                    'Diploma/Graduation marks cards and Certificate',
                    'Entrance test score card, if any',
                    'Work Experience Letter, if any',
                    'Any other Certificates, Specify:'
                ]
            }
        }
        try:
            page1_collection.update_one(
                {"application_number":application_number},
                {"$set":form_data},
                upsert=True
            )
            session['progress']['page1']=True
            session.modified = True

            lock_page1_for_user(application_number,'page1')
            return redirect(url_for('app_form.page2'))
        
        except ConnectionError as e:
            flash(f"Error Submitting data,Please try again!: {e}")
            return redirect(url_for('app_form.page1'))
        
    return render_template('page1.html')

def page2_locked(application_number):
    lock_status=page2_collection.find_one({"application_number":application_number,"locked":True})
    return lock_status is not None

def lock_page2_for_user(application_number,page_name):
    page2_collection.update_one(
        {"application_number":application_number},
        {"$set":{"locked":True}}
    )

@app_form.route('/page2', methods=['POST','GET'])
def page2():
    if 'signin' not in session or not session['signin']:
        return redirect(url_for('auth.signin'))
    if not session.get('progress', {}).get('page1'):
        return redirect(url_for('app_form.page1'))
    
    # check whether page2 already submitted
    application_number=session.get("application_number")

    if page1_locked(application_number) and page2_locked(application_number) and page3_locked(application_number) and page4_locked(application_number):
        flash('Application Submitted Successfully','success')
        return redirect(url_for('app_form.preview'))

    if page2_locked(application_number):
        flash('Page 2 is already submitted. You cannot edit it anymore.','error')
        return redirect(url_for('app_form.page3'))

    if request.method=='POST':
        application_number=session.get("application_number")
        admission_type=request.form.get("admission_type")
        pgcet_no=request.form.get("pgcet_no")
        admission_order_no=request.form.get("admission_order_no")
        rank=request.form.get("rank")
        claimed_category=request.form.get("claimed_category")
        allocated_category=request.form.get("allocated_category")
        locality=request.form.get("admission_type")
        first_name=request.form.get("first_name")
        middle_name=request.form.get("middle_name")
        surname=request.form.get("surname")
        dob=request.form.get("dob")
        gender=request.form.get("gender")
        nationality=request.form.get("nationality")
        religion=request.form.get("religion")
        blood_group=request.form.get("blood_group")
        physically_challenged=request.form.get("physically_challenged")
        category=request.form.get("category")
        aadhaar_no=request.form.get("aadhaar_no")
        father_name=request.form.get("father_name")
        mother_name=request.form.get("mother_name")
        father_occupation=request.form.get("father_occupation")
        mother_occupation=request.form.get("mother_occupation")
        father_phone=request.form.get("father_phone")
        mother_phone=request.form.get("mother_phone")
        correspondence_city=request.form.get("correspondence_city")
        correspondence_pincode=request.form.get("correspondence_pincode")
        correspondence_state=request.form.get("correspondence_state")
        correspondence_country=request.form.get("correspondence_country")
        correspondence_tel=request.form.get("correspondence_tel")
        correspondence_mobile=request.form.get("correspondence_mobile")
        permanent_city=request.form.get("permanent_city")
        permanent_pincode=request.form.get("permanent_pincode")
        permanent_state=request.form.get("permanent_state")
        permanent_country=request.form.get("permanent_country")
        permanent_tel=request.form.get("permanent_tel")
        permanent_mobile=request.form.get("permanent_mobile")
        preferred_contact_time=request.form.get("preferred_contact_time")
        passport=request.form.get("passport")
        passport_no=request.form.get("passport_no")
        passport_expiry=request.form.get("passport_expiry")
        passport_issued_on=request.form.get("passport_issued_on")



        form_data = {
            "application_number": str(application_number) if isinstance(application_number, ObjectId) else application_number,
            "admission_type":admission_type ,
            "pgcet_no":pgcet_no,
            "admission_order_no": admission_order_no,
            "rank": rank,
            "claimed_category":claimed_category ,
            "allocated_category":allocated_category ,
            "locality": locality,
            "first_name": first_name,
            "middle_name":middle_name ,
            "surname": surname,
            "dob":dob ,
            "gender": gender,
            "nationality":nationality ,
            "religion": religion,
            "blood_group":blood_group ,
            "physically_challenged":physically_challenged ,
            "category":category ,
            "aadhaar_no": aadhaar_no,
            "father_name":father_name,
            "mother_name":mother_name ,
            "father_occupation": father_occupation,
            "mother_occupation": mother_occupation,
            "father_phone": father_phone,
            "mother_phone":mother_phone ,
            "correspondence_city":correspondence_city ,
            "correspondence_pincode":correspondence_pincode ,
            "correspondence_state":correspondence_state,
            "correspondence_country":correspondence_country ,
            "correspondence_tel": correspondence_tel,
            "correspondence_mobile":correspondence_mobile,
            "permanent_city": permanent_city,
            "permanent_pincode":permanent_pincode ,
            "permanent_state": permanent_state,
            "permanent_country": permanent_country,
            "permanent_tel": permanent_tel,
            "permanent_mobile":permanent_mobile ,
            "preferred_contact_time":preferred_contact_time ,
            "passport": passport,
            "passport_no": passport_no,
            "passport_expiry":passport_expiry ,
            "passport_issued_on": passport_issued_on
        }
   
        # required_fields = [
        #     "pgcet_no", "admission_order_no", "rank", 
        #     "claimed_category", "allocated_category", "locality", 
        #     "first_name", "surname", "dob", "gender", "nationality", 
        #     "religion", "blood_group", "physically_challenged", 
        #     "category", "aadhaar_no", "father_name", "mother_name", 
        #     "father_occupation", "mother_occupation", "father_phone", 
        #     "mother_phone", "correspondence_city", "correspondence_pincode", 
        #     "correspondence_state", "correspondence_country", 
        #     "correspondence_mobile", "permanent_city", "permanent_pincode", 
        #     "permanent_state", "permanent_country", "permanent_mobile", 
        #     "preferred_contact_time", "passport"
        # ]

        # if request.form.get("passport") == "yes":
        #     required_fields += ["passport_no", "passport_expiry", "passport_issued_on"]

        # if any(form_data[field] == "" for field in required_fields):
        #     flash("Please enter the details in all the required fields.", "error")
        #     return render_template('page2.html', form_data=form_data)
        
        try:
            page2_collection.update_one(
                {"application_number":application_number},
                {"$set":form_data},
                upsert=True   #if application number doesn't exists it vl create
            )
            session['progress']['page2']=True
            session.modified = True

            # locks page for further editing
            lock_page2_for_user(application_number,'page2')

            return redirect(url_for('app_form.page3'))
        except Exception as e:
            flash(f"Error while submitting data.Please try again!{e}",'error')
            return render_template('page2.html', form_data=form_data)
        
    return render_template('page2.html')

def page3_locked(application_number):
    lock_status=page3_collection.find_one({"application_number":application_number,"locked":True})
    return lock_status is not None

def lock_page3_for_user(application_number,page_name):
    page3_collection.update_one(
        {"application_number":application_number},
        {"$set":{"locked":True}}
    )

@app_form.route('/page3',methods=['POST','GET'])
def page3():
    if 'signin' not in session or not session['signin']:
        return redirect(url_for('auth.signin'))
    if not session.get('progress', {}).get('page2'):
        return redirect(url_for('app_form.page2'))
    
    application_number=session.get("application_number")

    if page1_locked(application_number) and page2_locked(application_number) and page3_locked(application_number) and page4_locked(application_number):
        flash('Application Submitted Successfully','success')
        return redirect(url_for('app_form.preview'))
    
    if page3_locked(application_number):
        flash('Page 3 is already submitted. You cannot edit it anymore.','error')
        return redirect(url_for('app_form.page4'))
    if request.method=='POST':
        try:
            education_data ={
                "10th_standard":{
                    "course":request.form.get("course_10"),
                    "board_university":request.form.get("board_university_10"),
                    "college_name":request.form.get("college_name_10"),
                    "year_from":request.form.get("year_from_10"),
                    "year_to": request.form.get("year_to_10"),
                    "grade": request.form.get("grade_10")
                },
                "12th_standard": {
                    "course": request.form.get("course_12"),
                    "board_university": request.form.get("board_university_12"),
                    "college_name": request.form.get("college_name_12"),
                    "year_from": request.form.get("year_from_12"),
                    "year_to": request.form.get("year_to_12"),
                    "grade": request.form.get("grade_12")
                },
                "graduation": {
                    "course": request.form.get("course_ug"),
                    "board_university": request.form.get("board_university_ug"),
                    "college_name": request.form.get("college_name_ug"),
                    "year_from": request.form.get("year_from_ug"),
                    "year_to": request.form.get("year_to_ug"),
                    "grade": request.form.get("grade_ug")
                },
                "post_graduation": {
                    "course": request.form.get("course_pg"),
                    "board_university": request.form.get("board_university_pg"),
                    "college_name": request.form.get("college_name_pg"),
                    "year_from": request.form.get("year_from_pg"),
                    "year_to": request.form.get("year_to_pg"),
                    "grade": request.form.get("grade_pg")
                },
                "others": {
                    "course": request.form.get("course_ot"),
                    "board_university": request.form.get("board_university_ot"),
                    "college_name": request.form.get("college_name_ot"),
                    "year_from": request.form.get("year_from_ot"),
                    "year_to": request.form.get("year_to_ot"),
                    "grade": request.form.get("grade_ot")
                }
            }
            work_experience_data = {
                'work_experience': request.form.get('work_experience'),
                'total_years': request.form.get('total_years'),
                'work_from': request.form.get('work_from'),
                'work_to': request.form.get('work_to'),
                'organization': request.form.get('organization'),
                'awards': request.form.get('awards'),
                'interests': request.form.get('interests'),
            }

            finance_data = {
                'family_income': request.form.get('family_income'),
                'finance_source': request.form.getlist('finance_source'),
            }

            entrance_test_data = {
                'entrance_test': request.form.getlist('entrance_test'),
                'other_tests_specify': request.form.get('other_tests_specify'),
                'test_score': request.form.get('test_score'),
                'registration_no': request.form.get('registration_no'),
                'exam_date': request.form.get('exam_date'),
                'no_exams': 'no_exams' in request.form,
            }

            # Combine all data into a single document
            form_data = {
                "application_number":session.get("application_number"),
                'education': education_data,
                'work_experience': work_experience_data,
                'finance': finance_data,
                'entrance_tests': entrance_test_data,
            }
            

            # Insert data into MongoDB collection
            try:
                page3_collection.update_one(
                {"application_number":application_number},
                {"$set":form_data},
                upsert=True   #if application number doesn't exists it vl create
            )
                session['progress']['page3']=True
                session.modified = True

                lock_page3_for_user(application_number,'page3')

                return redirect(url_for('app_form.page4'))
            except Exception as e:
                flash('Error While submitting the data, Please try again!',e)
                return redirect(url_for('app_form.page3'))
        except Exception as e:
            flash('Error While submitting the data, Please try again!',e)
            return redirect(url_for('app_form.page3'))
    
    # page2_data=session.get('page2_data',{})
    return render_template("page3.html")

def page4_locked(application_number):
    lock_status=page4_collection.find_one({"application_number":application_number,"locked":True})
    return lock_status is not None

def lock_page4_for_user(application_number,page_name):
    page4_collection.update_one(
        {"application_number":application_number},
        {"$set":{"locked":True}}
    )

@app_form.route('/page4',methods=['GET','POST'])
def page4():
    if not session.get('progress', {}).get('page3'):
        return redirect(url_for('app_form.page3'))
    
    if 'signin' not in session or not session['signin']:
        return redirect(url_for('auth.signin'))
    
    application_number=session.get("application_number")

    if page1_locked(application_number) and page2_locked(application_number) and page3_locked(application_number) and page4_locked(application_number):
        flash('Application Submitted Successfully','success')
        return redirect(url_for('app_form.preview'))
    
    if page4_locked(application_number):
        flash('Final Submission of application is done. You cannot edit it anymore.','error')
        return redirect(url_for('app_form.preview'))
    
    if request.method=="POST":
        # Insert data into MongoDB collection
            try:
                page4_collection.insert_one({"application_number":application_number})
                session['progress']['page4']=True
                session.modified = True

                lock_page4_for_user(application_number,'page4')

                return redirect(url_for('app_form.preview'))
            except Exception as e:
                flash('Error While submitting the data, Please try again!',e)
                return redirect(url_for('app_form.page4'))

    return render_template("page4.html")

@app_form.route('/preview', methods=['GET'])
def preview():
    application_number =session.get("application_number")
    page1_data=page1_collection.find_one({'application_number':application_number})
    page2_data=page2_collection.find_one({'application_number':application_number})
    page3_data=page3_collection.find_one({'application_number':application_number})

    entire_form_data={
        'page1_data':page1_data,
        'page2_data':page2_data,
        'page3_data':page3_data
    }

    return render_template('preview.html',data=entire_form_data)

@app_form.route('/download_pdf', methods=['POST'])
def download_pdf():
    # Get application number from form submission
    application_number = request.form.get("application_number")
    
    # Fetch the form data for the given application number
    page1_data = page1_collection.find_one({'application_number': application_number})
    page2_data = page2_collection.find_one({'application_number': application_number})
    page3_data = page3_collection.find_one({'application_number': application_number})

    # Combine the data into a dictionary
    entire_form_data = {
        'page1_data': page1_data,
        'page2_data': page2_data,
        'page3_data': page3_data
    }

    # Render the HTML content for the PDF
    rendered_html = render_template('preview.html', data=entire_form_data)

    # Inject custom CSS for PDF rendering
    pdf_css_url = url_for('static', filename='css/pdf_styles.css')

    rendered_html = f"""
    <html>
    <head>
        <link rel="stylesheet" href="{pdf_css_url}">
    </head>
    <body>
        {rendered_html}
    </body>
    </html>
    """

    # Create a BytesIO stream to hold the PDF data
    pdf_stream = io.BytesIO()

    # Convert the rendered HTML to PDF
    pisa_status = pisa.CreatePDF(io.StringIO(rendered_html), dest=pdf_stream)

    # Check for PDF generation errors
    if pisa_status.err:
        return "Error creating PDF", 500

    # Rewind the BytesIO stream
    pdf_stream.seek(0)

    # Create a response object and set the appropriate headers for PDF download
    response = make_response(pdf_stream.read())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=Application_{application_number}.pdf'

    return response


# @app_form.route('/download_pdf', methods=['POST'])
# def download_pdf():
#     application_number = request.form.get('application_number')
    
#     # Fetch data and generate PDF as shown in your previous code
#     page1_data = page1_collection.find_one({'application_number': application_number})
#     page2_data = page2_collection.find_one({'application_number': application_number})
#     page3_data = page3_collection.find_one({'application_number': application_number})

#     entire_form_data = {
#         'page1_data': page1_data,
#         'page2_data': page2_data,
#         'page3_data': page3_data
#     }
    
#     entire_form_data = convert_objectid_to_str(entire_form_data)

#     # Create a PDF
#     pdf_buffer = io.BytesIO()
#     pdf = canvas.Canvas(pdf_buffer, pagesize=letter)
#     pdf.setTitle('Form Preview')

#     for page, data in entire_form_data.items():
#         text = pdf.beginText(40, 750)  # Start position (x, y)
#         text.setFont("Helvetica", 12)
#         text.textLine(f"{page.capitalize()}:")
        
#         for key, value in data.items():
#             text.textLine(f"{key}: {value}")
        
#         pdf.drawText(text)
#         pdf.showPage()  # Move to the next page after each section

#     pdf.save()
#     pdf_buffer.seek(0)

#     return send_file(pdf_buffer, as_attachment=True, download_name='NCET-PG Application.pdf')


def convert_objectid_to_str(data):
    if isinstance(data, list):
        return [convert_objectid_to_str(item) for item in data]
    elif isinstance(data, dict):
        return {key: convert_objectid_to_str(value) for key, value in data.items()}
    elif isinstance(data, ObjectId):
        return str(data)
    else:
        return data

