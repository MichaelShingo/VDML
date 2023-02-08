from flask import Flask, render_template, flash, request, redirect, url_for, request, redirect, render_template
from flask import request
import sys, os, webbrowser, pyperclip
from werkzeug.utils import secure_filename
from scripts import lateEquipment, lateFinesCsv, lateFinesCirculationEmail, lateFinesUserEmail
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_fontawesome import FontAwesome
from flask_bootstrap import Bootstrap

print(sys.path)
# virtualenv env 
# cmd "source env/bin/activate"

#TODO filter by date added but descnding so you see most recent ones 
#TODO allow sorting after searching and filtering is set
#TODO edit userEmailGenerator to say less than 1 day late, vs. more than 1 day late 
#TODO fix date added to be a datetime object
#TODO add export csv option
#TODO poster printing receipt generator
#TODO booking analysis with visualization data dashboard

UPLOAD_FOLDER = './uploads/'
ALLOWED_EXTENSIONS = {'.csv'}
SQLALCHEMY_TRACK_MODIFICATIONS = False #you need this? 

db = SQLAlchemy() #initialize database
app = Flask(__name__) #references this file
Bootstrap(app)
fa = FontAwesome(app)
app.secret_key = 'jj8^^83jd)))ueid9ieSHI!!'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db' #three /'s is relative path, 4 is absolute path
db.init_app(app)

class LateFine(db.Model): #Todo is the table name, it's automatically lowercase when it's created
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    penn_id = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Integer, default=0, nullable=False)
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
sortingParameter = '' #database column name
sortingOrder = '' #asc or desc
searchIDList = []

def searchDatabase(searchTerm):
    global searchIDList
    searchIDList = []
    allEntries = LateFine.query.all()
    for entry in allEntries:
        entryString = (entry.name + entry.penn_id + entry.email + str(entry.amount) + entry.details + entry.schedule + str(entry.return_time) + entry.operator + str(entry.date_sent) + entry.forgiven).lower()
        if searchTerm in entryString:
            searchIDList.append(entry.id)
    return LateFine.query.filter(LateFine.id.in_(searchIDList)).all()

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
    global searchIDList
    for entry in currentDB:
        if entry.selected:
            selectedSet.add(entry.id)

    if request.method == 'POST':
        if 'add-entry' in request.form:
            text = request.form['text']
            owner, bookingNum, equipmentString, dateRange, returnTime, staffName, todayDate = ['', '', '', '', '', '', '']

            try:
                if not text == '':
                    owner, bookingNum, equipmentString, dateRange, returnTime, staffName, todayDate = lateFinesCsv.generateCSV(text)

            except Exception as e:
                print(e)
                flash('Error: The script failed to extract data from pasted text. Blank fields added.')

            pennID = request.form['penn-id']
            email = request.form['user-email']
            amount = request.form['fine-amount']
            forgiven = request.form['forgiven']
            new_entry = LateFine(name=owner, penn_id=pennID, email=email, amount=amount, booking_number=bookingNum, 
                details=equipmentString, schedule=dateRange, return_time=returnTime, operator=staffName, forgiven=forgiven)

            db.session.add(new_entry)
            db.session.commit()
            return redirect('/late_fines')
        
        elif 'update-entry' in request.form:
            idToUpdate = request.form['id-to-update']
            lateFine = LateFine.query.get_or_404(idToUpdate) #how to pass the id here? 
            lateFine.name = request.form['name']
            lateFine.penn_id = request.form['penn-id']
            lateFine.email = request.form['email']
            lateFine.amount = request.form['amount']
            lateFine.booking_number = request.form['booking_number']
            lateFine.details = request.form['details']
            lateFine.schedule = request.form['schedule']
            lateFine.return_time = request.form['return_time']
            lateFine.operator = request.form['operator']
            lateFine.date_sent = request.form['date_sent']
            lateFine.forgiven = request.form['forgiven']
            db.session.commit()
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
            #global searchIDList
            searchIDList = []
            tasks = LateFine.query.all()
            return render_template('late_fines.html', tasks=tasks, cols='0', visibility='hidden', visibilityCSV='hidden', visibilityUser='hidden', visibilityCirc='hidden')
        elif 'search' in request.form:
            searchTerm = request.form['search'].lower()
            tasks = searchDatabase(searchTerm)

            return render_template('late_fines.html', tasks=tasks, cols='0', visibility='hidden', visibilityCSV='hidden', visibilityUser='hidden', visibilityCirc='hidden')
                

    else:
        if len(searchIDList) > 0:
            print('search ID list -------------')
            tasks = LateFine.query.filter(LateFine.id.in_(searchIDList)).all()

        elif sortingParameter:
            print(f'--SORTING PARAMETER = {sortingParameter}--')
            if sortingParameter == 'name' and sortingOrder == 'desc':
                tasks = LateFine.query.order_by(LateFine.name.desc()).all() 
            elif sortingParameter == 'name' and sortingOrder == 'asc':
                tasks = LateFine.query.order_by(LateFine.name.asc()).all()
            elif sortingParameter == 'email' and sortingOrder == 'desc':
                tasks = LateFine.query.order_by(LateFine.email.desc()).all()
            elif sortingParameter == 'email' and sortingOrder == 'asc':
                tasks = LateFine.query.order_by(LateFine.email.asc()).all()
            elif sortingParameter == 'amount' and sortingOrder == 'desc':
                tasks = LateFine.query.order_by(LateFine.amount.desc()).all()
            elif sortingParameter == 'amount' and sortingOrder =='asc':
                tasks = LateFine.query.order_by(LateFine.amount.asc()).all()
            elif sortingParameter == 'booking' and sortingOrder == 'desc':
                tasks = LateFine.query.order_by(LateFine.booking_number.desc()).all()
            elif sortingParameter == 'booking' and sortingOrder =='asc':
                tasks = LateFine.query.order_by(LateFine.booking_number.asc()).all()
            elif sortingParameter == 'return_time' and sortingOrder == 'desc':
                tasks = LateFine.query.order_by(LateFine.return_time.desc()).all()
            elif sortingParameter == 'return_time' and sortingOrder == 'asc':
                tasks = LateFine.query.order_by(LateFine.return_time.asc()).all()
            elif sortingParameter == 'operator' and sortingOrder == 'desc':
                tasks = LateFine.query.order_by(LateFine.operator.desc()).all()
            elif sortingParameter == 'operator' and sortingOrder == 'asc':
                tasks = LateFine.query.order_by(LateFine.operator.asc()).all()
            elif sortingParameter == 'date_sent' and sortingOrder == 'desc':
                tasks = LateFine.query.order_by(LateFine.date_sent.desc()).all()
            elif sortingParameter == 'date_sent' and sortingOrder == 'asc':
                tasks = LateFine.query.order_by(LateFine.date_sent.asc()).all()

        else:
            tasks = LateFine.query.order_by(LateFine.date_sent).all() #returns all 

        try:
            return render_template('late_fines.html', tasks=tasks, cols='0', visibility='hidden', visibilityCSV='hidden', visibilityUser='hidden', visibilityCirc='hidden')
        except:
            #if table todo does not exist, create table
            tasks = LateFine.query.order_by(LateFine.date_sent).all() #returns all 
            return render_template('late_fines.html', tasks=tasks, cols='0', visibility='hidden', visibilityCSV='hidden', visibilityUser='hidden', visibilityCirc='hidden')

# @app.route('/search')
# def search():
entryToUpdateID = -1

# @app.route('/update/<int:id>', methods=['GET', 'POST'])
# def update(id):
#     print('udpate route')
#     tasks = LateFine.query.order_by(LateFine.date_sent).all()
#     global entryToUpdateID
#     entryToUpdateID = id
#     return render_template('late_fines.html', visibilityUpdate='visible', tasks=tasks, cols='0', visibility='hidden', visibilityCSV='hidden', visibilityUser='hidden', visibilityCirc='hidden')

#     task = LateFine.query.get_or_404(id)
#     if request.method == 'POST':
#         task.name = request.form['name']
#         task.penn_id = request.form['penn_id']
#         task.email = request.form['email']
#         task.amount = request.form['amount']
#         task.booking_number = request.form['booking_number']
#         task.details = request.form['details']
#         task.schedule = request.form['schedule']
#         task.return_time = request.form['return_time']
#         task.operator = request.form['operator']
#         task.date_sent = request.form['date_sent']
#         task.forgiven = request.form['forgiven']
#         try:
#             db.session.commit()
#             return redirect('/late_fines')
#         except:
#             return 'There was an issue updating your task'
#     else:
#         #get all field values rendered in editable inputs 
#         return render_template('late_fines.html', tasks=tasks, cols='0', visibility='hidden', visibilityCSV='hidden', visibilityUser='hidden', visibilityCirc='hidden')

#         return render_template('update.html', task=task)

       
@app.route('/sort-desc-name')
def sortDescName():
    print('---SORT DESCENDING BY NAME')
    global sortingParameter
    global sortingOrder
    sortingParameter = 'name'
    sortingOrder = 'desc'
   
    return redirect('/late_fines')

@app.route('/sort-asc-name')
def sortAscName():
    global sortingParameter
    global sortingOrder
    sortingParameter = 'name'
    sortingOrder = 'asc'
    return redirect('/late_fines')

@app.route('/sort-desc-email')
def sortDescEmail():
    global sortingParameter
    global sortingOrder
    sortingParameter = 'email'
    sortingOrder = 'desc'
    return redirect('/late_fines')

@app.route('/sort-asc-email')
def sortAscEmail():
    global sortingParameter
    global sortingOrder
    sortingParameter = 'email'
    sortingOrder = 'asc'
    return redirect('/late_fines')

@app.route('/sort-desc-amount')
def sortDescAmount():
    global sortingParameter
    global sortingOrder
    sortingParameter = 'amount'
    sortingOrder = 'desc'
    return redirect('/late_fines')

@app.route('/sort-asc-amount')
def sortAscAmount():
    global sortingParameter
    global sortingOrder
    sortingParameter = 'amount'
    sortingOrder = 'asc'
    return redirect('/late_fines')

@app.route('/sort-desc-booking')
def sortDescBooking():
    global sortingParameter
    global sortingOrder
    sortingParameter = 'booking'
    sortingOrder = 'desc'
    return redirect('/late_fines')

@app.route('/sort-asc-booking')
def sortAscBooking():
    global sortingParameter
    global sortingOrder
    sortingParameter = 'booking_number'
    sortingOrder = 'asc'
    return redirect('/late_fines')

@app.route('/sort-desc-return-time')
def sortDescReturnTime():
    global sortingParameter
    global sortingOrder
    sortingParameter = 'return_time'
    sortingOrder = 'desc'
    return redirect('/late_fines')

@app.route('/sort-asc-return-time')
def sortAscReturnTime():
    global sortingParameter
    global sortingOrder
    sortingParameter = 'return_time'
    sortingOrder = 'asc'
    return redirect('/late_fines')

@app.route('/sort-desc-staff')
def sortDescStaff():
    global sortingParameter
    global sortingOrder
    sortingParameter = 'operator'
    sortingOrder = 'desc'
    return redirect('/late_fines')

@app.route('/sort-asc-staff')
def sortAscStaff():
    global sortingParameter
    global sortingOrder
    sortingParameter = 'operator'
    sortingOrder = 'asc'
    return redirect('/late_fines')

@app.route('/sort-desc-date-sent')
def sortDescDateSent():
    global sortingParameter
    global sortingOrder
    sortingParameter = 'date_sent'
    sortingOrder = 'desc'
    return redirect('/late_fines')

@app.route('/sort-asc-date-sent')
def sortAscDateSent():
    global sortingParameter
    global sortingOrder
    sortingParameter = 'date_sent'
    sortingOrder = 'asc'
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