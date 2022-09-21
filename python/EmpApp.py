from flask import Flask, render_template, request
from pymysql import connections
import os
import boto3
import io
from config import *
from matplotlib.pyplot import mpimg

app = Flask(__name__)

bucket = custombucket
region = customregion

db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
output = {}
table = 'employee'


@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('index.html')


@app.route("/about", methods=['POST'])
def about():
    return render_template('www.intellipaat.com')


@app.route("/addemp", methods=['POST'])
def AddEmp():
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    pri_skill = request.form['pri_skill']
    location = request.form['location']
    emp_image_file = request.files['emp_image_file']
    emp_resume_file = request.files['emp_resume_file']

    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    if emp_image_file.filename == "":
        return "Please select a file"

    try:

        cursor.execute(insert_sql, (emp_id, first_name, last_name, pri_skill, location))
        db_conn.commit()
        emp_name = "" + first_name + " " + last_name
        # Uplaod image file in S3 #
        emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
        emp_resume_name_in_s3 = "emp-id-" + str(emp_id) + "_resume"
        s3 = boto3.resource('s3')

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")
            s3.Bucket(custombucket).put_object(Key=emp_image_file_name_in_s3, Body=emp_image_file)
            s3.Bucket(custombucket).put_object(Key=emp_resume_name_in_s3, Body=emp_resume_file)
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                emp_image_file_name_in_s3)

        except Exception as e:
            return str(e)

    finally:
        cursor.close()

    print("all modification done...")
    return render_template('add_employees_successful.html', name=emp_name)

@app.route("/fetchdata", methods=['POST'])
def FetchData():
    emp_id = request.form['emp_id']

    query = "SELECT * FROM <TABLE_NAME> WHERE emp_id = %s"
    cursor = db_conn.cursor()

    try:

        details = cursor.execute(query, emp_id)
        for detail in details:
            var = detail

        # Declaring the image file name
        emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
        emp_resume_name_in_s3 = "emp-id-" + str(emp_id) + "_resume"
        s3 = boto3.resource('s3')

        try:
            object = bucket.Object(emp_image_file_name_in_s3) 
            file_stream = io.StringIO() 
            object.download_fileobj(file_stream) 
            img = mpimg.imread(file_stream)

        except Exception as e:
            return str(e)

    finally:
        cursor.close()

    print("all modification done...")
    return render_template('add_employees_successful.html', 
                           id=emp_id, 
                           var=var,
                           image_url=img)

@app.route("/update", methods=['POST'])
def UpdateEmp():
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    pri_skill = request.form['pri_skill']
    location = request.form['location']
    emp_image_file = request.files['emp_image_file']
    emp_resume_file = request.files['emp_resume_file']

    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    if emp_image_file.filename == "":
        return "Please select a file"

    if emp_resume_file.filename == "":
        return "Please select a file"

    try:

        cursor.execute(insert_sql, (emp_id, first_name, last_name, pri_skill, location))
        db_conn.commit()
        emp_name = "" + first_name + " " + last_name
        # Uplaod image file in S3 #
        emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
        emp_resume_name_in_s3 = "emp-id-" + str(emp_id) + "_resume"
        s3 = boto3.resource('s3')

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")
            s3.Bucket(custombucket).put_object(Key=emp_image_file_name_in_s3, Body=emp_image_file)
            s3.Bucket(custombucket).put_object(Key=emp_resume_name_in_s3, Body=emp_resume_file)
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

            object1_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                emp_image_file_name_in_s3)

            object2_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                emp_resume_name_in_s3)

        except Exception as e:
            return str(e)

    finally:
        cursor.close()

    print("all modification done...")
    return render_template('show_employee_data.html', 
                            id=emp_id)
    
@app.route("/delete", methods=['POST'])
def DeleteEmp():
    emp_id = request.form['emp_id']

    query = "DELETE FROM employee WHERE emp_id=%s)"
    cursor = db_conn.cursor()

    try:

        cursor.execute(query, emp_id)
        db_conn.commit()
        # Uplaod image file in S3 #
        emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
        emp_resume_name_in_s3 = "emp-id-" + str(emp_id) + "_resume"
        s3 = boto3.resource('s3')

        try:
            print("Data removed from MySQL RDS... deleting related files in S3...")
            s3.Object(custombucket, emp_image_file_name_in_s3).delete()
            s3.Object(custombucket, emp_resume_name_in_s3).delete()

        except Exception as e:
            return str(e)

    finally:
        cursor.close()

    print("all modification done...")
    return render_template('delete_employees_successful.html', id=emp_id)
    
        

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
