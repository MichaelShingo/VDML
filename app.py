from flask import Flask, render_template, flash, request, redirect, url_for, request, redirect, render_template
from flask import request
import sys, os, webbrowser, pyperclip
from werkzeug.utils import secure_filename
from scripts import lateEquipment, lateFinesCsv, lateFinesCirculationEmail, lateFinesUserEmail
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_fontawesome import FontAwesome

print(sys.path)
# virtualenv env 
# cmd "source env/bin/activate"

#TODO fix date added to be a datetime object
#TODO add sorting features
#TODO add export csv option
#TODO add error catching if text is blank
#TODO labels on update page, larger textarea for late equipment and notes
#TODO deselect all button

#TODO poster printing receipt generator
#TODO booking analysis with visualization data dashboard

UPLOAD_FOLDER = './uploads/'
ALLOWED_EXTENSIONS = {'.csv'}
SQLALCHEMY_TRACK_MODIFICATIONS = False #you need this? 

db = SQLAlchemy() #initialize database
app = Flask(__name__) #references this file
fa = FontAwesome(app)
app.secret_key = 'jj8^^83jd)))ueid9ieSHI!!'

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
    db.create_all()



@app.route('/')  #routes to index.html so you don't 404
def index():
    return render_template('index.html')


selectedSet = set()
sortingParameter = ''


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

    currentDB = LateFine.query.all()

    for entry in currentDB:
        if entry.selected:
            selectedSet.add(entry.id)

    if request.method == 'POST':
        if 'add-entry' in request.form:
            text = request.form['text']
            try:
                owner, bookingNum, equipmentString, dateRange, returnTime, staffName, todayDate = lateFinesCsv.generateCSV(text)
                pennID = request.form['penn-id']
                email = request.form['user-email']
                amount = request.form['fine-amount']
                forgiven = request.form['forgiven']

                new_entry = LateFine(name=owner, penn_id=pennID, email=email, amount=amount, booking_number=bookingNum, 
                    details=equipmentString, schedule=dateRange, return_time=returnTime, operator=staffName, forgiven=forgiven)

                db.session.add(new_entry)
                db.session.commit()
            except:
                flash('The script failed to extract data from pasted text.')
            return redirect('/late_fines')

        elif 'generate-emails' in request.form:
            tasks = LateFine.query.order_by(LateFine.date_sent).all()
            resultUser = ''
            resultCirc = ''
            for id in selectedSet:
                currentEntry = LateFine.query.get_or_404(id)
                resultUser += lateFinesUserEmail.generateEmail(currentEntry.name, currentEntry.amount, currentEntry.details, 
                    currentEntry.schedule, currentEntry.return_time) + '\n\n'
                resultCirc += f'''{currentEntry.name}\n{currentEntry.penn_id}\n{currentEntry.email}\n${currentEntry.amount}\n{currentEntry.booking_number}\n{currentEntry.details}\n\n-----------------------------------------\n'''
                
            return render_template('late_fines.html', methods=['POST'], visibilityUser='visible', resultTextCirc=resultCirc, resultTextUser=resultUser,
                visibilityCSV='hidden', visbilityCirc='hidden', tasks=tasks)
        elif 'deselect-all' in request.form:
            for id in selectedSet:
                currentEntry = LateFine.query.get_or_404(id)
                currentEntry.selected = False
            db.session.commit()
            selectedSet.clear()
            return redirect('/late_fines')
        elif 'select-all' in request.form:
            for entry in currentDB:
                entry.selected = True
                selectedSet.add(entry.id)
            db.session.commit()
            return redirect('/late_fines')
        elif 'filter-by-date-added' in request.form:
            tasks = LateFine.query.filter_by(date_sent='2023-01-26').all()#added-date'])
            return render_template('late_fines.html', tasks=tasks, cols='0', visibility='hidden', visibilityCSV='hidden', visibilityUser='hidden', visibilityCirc='hidden')
        elif 'clear-filters' in request.form:
            return redirect('/late_fines')



    else:
        # if sortingParameter:
        #     if sortingParameter == 'name':
        #         sortingDBObject = LateFine.name
        #     elif sortingParameter == 'email':
        #         sortingDBObject = LateFine.email
        #     elif sortingParameter == '':
        #         sortingDBObject == LateFine.date_sent
        
        try:
            tasks = LateFine.query.order_by(sortingDBObject).all() #returns all 
            return render_template('late_fines.html', tasks=tasks, cols='0', visibility='hidden', visibilityCSV='hidden', visibilityUser='hidden', visibilityCirc='hidden')
        except:
            #if table todo does not exist, create table
            tasks = LateFine.query.order_by(LateFine.date_sent).all() #returns all 

            return render_template('late_fines.html', tasks=tasks, cols='0', visibility='hidden', visibilityCSV='hidden', visibilityUser='hidden', visibilityCirc='hidden')

@app.route('/sort-desc-name')
def sortDescName():
    sortingParameter = 'name'
    return redirect('/late_fines')

@app.route('/sort-asc-name')
def sortAscName():
    return redirect('/late_fines')

@app.route('/delete/<int:id>') 
def delete(id):
    task_to_delete = LateFine.query.get_or_404(id)
    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/late_fines')
    except:
        return 'There was a problem deleting that task'

@app.route('/select/<int:id>')
def select(id):
    entry = LateFine.query.get_or_404(id)
    if not id in selectedSet:
        selectedSet.add(id)
        entry.selected = True
    else:
        selectedSet.remove(id)
        entry.selected = False
    db.session.commit()
    print(f'CURRENT LIST = {selectedSet}')
    return redirect('/late_fines')

@app.route('/generateUserEmail/<int:id>')
def generateUserEmail(id):
    currentEntry = LateFine.query.get_or_404(id)
    subjectLine = 'Vitale Digital Media Lab - Late Fine'
    userEmail = currentEntry.email
    resultUser = lateFinesUserEmail.generateEmail(currentEntry.name, currentEntry.amount, currentEntry.details, currentEntry.schedule, currentEntry.return_time)
    webbrowser.open(f'mailto:{userEmail}?Subject=Vitale Digital Media Lab - Late Fine&body={resultUser}')
    #flash('Email for the user was copied to your clipboard.')
    pyperclip.copy(resultUser)
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