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

class LateFine(db.Model): #Todo is the table name, it's automatically lowercase when it's created
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    penn_id = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    booking_number = db.Column(db.String(200), nullable=False)
    details = db.Column(db.String(200), nullable=False)
    schedule = db.Column(db.String(200), nullable=False)
    return_time = db.Column(db.String(200), nullable=False)
    operator = db.Column(db.String(200), nullable=False)
    date_sent = db.Column(db.String(200), default=(datetime.utcnow()).strftime('%Y-%m-%d')) #2023-01-25 15:04:04.443131
    forgiven = db.Column(db.String(200), nullable=False)
    selected = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return '<Task %r>' % self.id #when you create new element, it returns the task and the id of the task created 


with app.app_context():
    print('created database')
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
def late_fines(visibility='hidden', cols='0', resulTextCSV=None, visibilityCSV='hidden', visibilityUser='hidden', visbilityCirc='hidden'):
    #add select button on database, adds LateFine object to list
    #click on generate emails
    #loop through list and run script for each 
    select = 'Select'

    if request.method == 'POST':
        if 'add-entry' in request.form:
            text = request.form['text']
            owner, bookingNum, equipmentString, dateRange, returnTime, staffName, todayDate = lateFinesCsv.generateCSV(text)
            pennID = request.form['penn-id']
            email = request.form['user-email']
            amount = request.form['fine-amount']
            forgiven = request.form['forgiven']
            processed_text = 'temp text'

            new_entry = LateFine(name=owner, penn_id=pennID, email=email, amount=amount, booking_number=bookingNum, 
                details=equipmentString, schedule=dateRange, return_time=returnTime, operator=staffName, forgiven=forgiven)

            db.session.add(new_entry)
            db.session.commit()
            return redirect('/late_fines')

        elif 'generate-emails' in request.form:
            text = request.form['text']
            processed_text = lateFinesUserEmail.generateEmail(text)
            return render_template('late_fines.html', originalTextUser=text, resultTextUser=processed_text, methods=['POST'], visibilityUser='visible',
                visibilityCSV='hidden', visbilityCirc='hidden')
    else:
        try:
            tasks = LateFine.query.order_by(LateFine.date_sent).all() #returns all 
            return render_template('late_fines.html', select=select, tasks=tasks, cols='0', visibility='hidden', visibilityCSV='hidden', visibilityUser='hidden', visibilityCirc='hidden')
        except:
            #if table todo does not exist, create table
            tasks = LateFine.query.order_by(LateFine.date_sent).all() #returns all 

            return render_template('late_fines.html', tasks=tasks, cols='0', visibility='hidden', visibilityCSV='hidden', visibilityUser='hidden', visibilityCirc='hidden')


@app.route('/delete/<int:id>') #id is primary key in database
def delete(id):
    task_to_delete = LateFine.query.get_or_404(id)
    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/late_fines')
    except:
        return 'There was a problem deleting that task'

selectedList = set()
@app.route('/select/<int:id>')
def select(id):
    entry = LateFine.query.get_or_404(id)
    if not id in selectedList:
        selectedList.add(id)
        entry.selected = True
    else:
        selectedList.remove(id)
        entry.selected = False
    db.session.commit()
    print(f'CURRENT LIST = {selectedList}')
    return redirect('/late_fines')


@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    task = LateFine.query.get_or_404(id)
    if request.method == 'POST':
        task.name = request.form['name']
        task.penn_id = request.form['penn_id']
        task.email = request.form['email']
        task.amount = request.form['amount']
        task.booking_number = request.form['booking_number']
        task.details = request.form['details']
        task.schedule = request.form['schedule']
        task.return_time = request.form['return_time']
        task.operator = request.form['operator']
        task.date_sent = request.form['date_sent']
        task.forgiven = request.form['forgiven']
        try:
            db.session.commit()
            return redirect('/late_fines')
        except:
            return 'There was an issue updating your task'
    else:
        #get all field values rendered in editable inputs 
        return render_template('update.html', task=task)



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