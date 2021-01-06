from flask import Flask, render_template, request, redirect, url_for
import os
from os.path import join, dirname, realpath

import pandas as pd
import mysql.connector

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="xl-solutions"
)

mycursor = mydb.cursor()

app = Flask(__name__)

# enable debugging mode
app.config["DEBUG"] = True

# Upload folder
UPLOAD_FOLDER = 'static/files'
app.config['UPLOAD_FOLDER'] =  UPLOAD_FOLDER


# Root URL
@app.route('/')
def index():
     # Set The upload HTML template '\templates\index.html'
    return render_template('index.html')

@app.route('/templates')  
def success():
     mycursor.execute("SELECT * FROM mobile_phones")
     data = mycursor.fetchall()
     return render_template('success.html', data=data)

@app.route('/templates')  
def fail():
     return render_template('fail.html')


# Get the uploaded files
@app.route("/", methods=['POST'])
def uploadFiles():
      # get the uploaded file
      uploaded_file = request.files['file']
      if uploaded_file.filename != '':
           file_path = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename)
          # set the file path
           uploaded_file.save(file_path)
           #save the file
           parseCSV(file_path)
           return redirect(url_for('success'))

def parseCSV(filePath):
      # CVS Column Names
      col_names = ['manufacturer' , 'model' , 'color' , 'carrier_plan_type' , 'quantity' , 'price']
      # Use Pandas to parse the CSV file
      csvData = pd.read_csv(filePath,names=col_names, header=None)    
      # Loop through the Rows
      if(csvData.isnull().sum().sum() == 0):
          if(len(csvData.columns)==6):
               for i, row in csvData.iterrows():
                    mycursor.execute("SELECT * FROM mobile_phones WHERE manufacturer = %s AND model = %s AND color = %s AND carrier_plan_type = %s ", (str(row['manufacturer']),str(row['model']),str(row['color']),str(row['carrier_plan_type'])))
                    search = mycursor.fetchone() #retorna o resultado da consulta ao banco
                    if search is not None: 
                         sql = "UPDATE mobile_phones SET quantity = %s , price = %s WHERE manufacturer = %s AND model = %s AND color = %s AND carrier_plan_type = %s"
                         value = (row['quantity'],row['price'],row['manufacturer'],row['model'],row['color'],row['carrier_plan_type'])
                         mycursor.execute(sql, value)
                         mydb.commit()
                    else:
                         sql = "INSERT INTO mobile_phones (manufacturer, model, color, carrier_plan_type, quantity, price) VALUES (%s, %s, %s, %s, %s, %s)"
                         value = (str(row['manufacturer']),str(row['model']),str(row['color']),str(row['carrier_plan_type']),row['quantity'],row['price'])
                         mycursor.execute(sql, value)
                         mydb.commit()
               return(True)
           
if (__name__ == "__main__"):
     app.run(port = 5000)