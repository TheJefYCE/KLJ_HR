from flask import Flask, render_template, request
from pymysql import connections
import os
import boto3
import io
from config import *
import matplotlib.image as mpimg
from matplotlib import pyplot as plt

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


@app.route("/")
def home():
    return render_template('index.html')


@app.route("/add", methods=['GET','POST'])
def addpage():
    return render_template('add_employees.html')

@app.route("/get", methods=['GET'])
def getpage():
    return render_template('get_employees.html')

@app.route("/up", methods=['GET'])
def updatepage():
    return render_template('update_employees.html')

@app.route("/del", methods=['GET'])
def deletepage():
    return render_template('delete_employees.html')

@app.route("/portfolio", methods=['GET'])
def aboutuspage():
    return render_template('portfolio.html')

@app.route("/addemp", methods=['GET','POST'])
def AddEmp():
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    pri_skill = request.form['pri_skill']
    location = request.form['location']
    emp_image_file = request.files['emp_image_file']

    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    if emp_image_file.filename == "":
        return "Please select a file"

    try:

        cursor.execute(insert_sql, (emp_id, first_name, last_name, pri_skill, location))
        db_conn.commit()
        emp_name = "" + first_name + " " + last_name
        # Uplaod image file in S3 #
        emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file.jpg"
        s3 = boto3.resource('s3')

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")
            s3.Bucket(custombucket).put_object(Key=emp_image_file_name_in_s3, Body=emp_image_file)
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

    print("successfully add one new employee...")
    return render_template('add_employees_successful.html', name=emp_name)

@app.route("/fetchdata", methods=['GET','POST'])
def FetchData():
    emp_id = request.form['emp_id']

    query = "SELECT * FROM employee WHERE emp_id=%s"
    cursor = db_conn.cursor()

    try:

        cursor.execute(query, emp_id)
        print('result get...')
        for result in cursor:
            print(result)

        # Declaring the image file name
        emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file.jpg"
        s3 = boto3.resource('s3')

        try:
            object = bucket.Object(emp_image_file_name_in_s3)

            object.download_file(emp_image_file_name_in_s3)

            img=mpimg.imread(emp_image_file_name_in_s3)

            imgplot = plt.imshow(img)

            plt.show(imgplot)

        except Exception as e:
            return str(e)

    finally:
        cursor.close()

    print("fetch employee data successfully...")
    return render_template('show_employee_data.html', image_url=imgplot, detail=result)

@app.route("/update", methods=['GET','POST'])
def UpdateEmp():
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    pri_skill = request.form['pri_skill']
    location = request.form['location']

    sql = "UPDATE employee SET first_name=%s, last_name=%s, pri_skill=%s, location=%s WHERE emp_id=%s"
    cursor = db_conn.cursor()

    try:

        cursor.execute(sql, (first_name, last_name, pri_skill, location, emp_id))
        db_conn.commit()

    finally:
        cursor.close()

    print("all modification done...")
    return render_template('index.html', 
                            id=emp_id)
    
@app.route("/delete", methods=['GET', 'POST'])
def DeleteEmp():
    emp_id = request.form['emp_id']

    query = "DELETE FROM employee WHERE emp_id=%s"
    cursor = db_conn.cursor()

    try:

        cursor.execute(query, emp_id)
        db_conn.commit()
        # Uplaod image file in S3 #
        emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file.jpg"
        s3 = boto3.resource('s3')

        try:
            print("Data removed from MySQL RDS... deleting related files in S3...")
            s3.Object(custombucket, emp_image_file_name_in_s3).delete()

        except Exception as e:
            return str(e)

    finally:
        cursor.close()

    print("delete employee successful...")
    return render_template('delete_employee_successful.html', id=emp_id)
    
        

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
