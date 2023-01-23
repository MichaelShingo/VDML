from flask import Flask, render_template, flash, request, redirect, url_for, request, redirect
from flask import request
import os
from werkzeug.utils import secure_filename
from scripts import lateEquipment, lateFinesCsv, lateFinesCirculationEmail, lateFinesUserEmail
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# virtualenv env 
# cmd "source env/bin/activate"
# TODO add a database, so you don't have to deal with excel and CSV's 


UPLOAD_FOLDER = './uploads/'
ALLOWED_EXTENSIONS = {'.csv'}



db = SQLAlchemy() #initialize database
app = Flask(__name__) #references this file

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db' #three /'s is relative path, 4 is absolute path
db.init_app(app)

class Todo(db.Model): #Todo is the table name, it's automatically lowercase when it's created
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Task %r>' % self.id #when you create new element, it returns the task and the id of the task created 


with app.app_context():
    db.create_all()



@app.route('/')  #routes to index.html so you don't 404
def index():
    return render_template('index.html')


@app.route("/late_equipment")
def late_equipment(visibility='hidden'):
    return render_template('late_equipment.html', visibility='hidden')

@app.route("/late_equipment", methods=['POST'])
def late_equipment_post(resultText=None, visibility='hidden'):
    text = request.form['text']
    processed_text = lateEquipment.generateEmail(text)
    return render_template('late_equipment.html', originalText=text, resultText=processed_text, methods=['POST'], visibility='visible')


@app.route("/late_fines", methods=['POST', 'GET'])
def late_fines(visibility='hidden', cols='0'):
    if request.method == 'POST':
        task_content = request.form['content']
        new_task = Todo(content=task_content)
        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('/late_fines')
        except:
            return 'There was an issue adding your task'
    else:
        try:
            tasks = Todo.query.order_by(Todo.date_created).all() #returns all 
            return render_template('late_fines.html', tasks=tasks, cols='0', visibility='hidden', visibilityCSV='hidden', visibilityUser='hidden', visibilityCirc='hidden')
        except:
            #if table todo does not exist, create table
            tasks = Todo.query.order_by(Todo.date_created).all() #returns all 

            return render_template('late_fines.html', tasks=tasks, cols='0', visibility='hidden', visibilityCSV='hidden', visibilityUser='hidden', visibilityCirc='hidden')

@app.route("/late_fines", methods=['POST', 'GET']) #posting means you send data somewhere, like a database
def late_fines_post(resulTextCSV=None, visibilityCSV='hidden', visibilityUser='hidden', visbilityCirc='hidden'):
    if 'csv' in request.form:
        text = request.form['text']
        processed_text = lateFinesCsv.generateCSV(text)
        return render_template('late_fines.html', originalTextCSV=text, resultTextCSV=processed_text, methods=['POST'], visibilityCSV='visible',
            visibilityUser='hidden', visibilityCirc='hidden')

    elif 'user-email' in request.form:
        text = request.form['text']
        processed_text = lateFinesUserEmail.generateEmail(text)
        return render_template('late_fines.html', originalTextUser=text, resultTextUser=processed_text, methods=['POST'], visibilityUser='visible',
            visibilityCSV='hidden', visbilityCirc='hidden')

    elif 'circ-email' in request.form:
        text = request.form['text']
        processed_text = lateFinesCirculationEmail.generateEmail(text)
        return render_template('late_fines.html', originalTextCirc=text, resultTextCirc=processed_text, methods=['POST'], 
            visibilityUser='hidden', visibilityCSV='hidden', visibilityCirc='visible')




def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

















@app.route('/booking_analysis', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        #check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('download_file', name=filename))
    return '''
     <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''


if __name__ == "__main__": # watches for changes and updates
    app.run(debug=True)