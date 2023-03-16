from flask import Flask, render_template, flash, request, redirect, url_for, request, redirect, render_template, make_response, send_from_directory
from functools import wraps
from flask import request
import os, webbrowser, json
from werkzeug.utils import secure_filename
from scripts import lateEquipment, lateFinesCsv, lateFinesCirculationEmail, lateFinesUserEmail, bookingAnalysis
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_fontawesome import FontAwesome
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from wtforms.validators import InputRequired
import csv

# ----- START VIRTUAL ENVIRONMENT AND COMMON GIT COMMANDS -----
# virtualenv env 
# cmd "source env/bin/activate"
# pip3 freeze > requirements.txt
# git pull -X theirs    (merge their changes)

# ----- PYTHON ANYWHERE -----
# If modules are not found upon deploy, go into virtual env, then pip install -r requirements.txt
# "workon myvirtualenv", then pip install packages from here
# If merge conflicts use this: maybe not because it overrides online database
#   git fetch --prune
#   git reset --hard origin/master

# ----- TASKS -----
# no decimals in charts (maybe set min Y value )
#TODOadd more comments, for future editing 
#TODO login information should be hashed...or store in .env? 
#TODO Explore selenium as a way of extracting data from connect2 directly

UPLOAD_FOLDER = './uploads/'
ALLOWED_EXTENSIONS = {'.csv'}
SQLALCHEMY_TRACK_MODIFICATIONS = False #you need this? 
SEPARATOR = '-----------------------------------------\n'

db = SQLAlchemy() #initialize database
app = Flask(__name__) #references this file
FontAwesome(app)
app.secret_key = 'jj8^^83jd)))ueid9ieSHI!!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///VDML.db' #three /'s is relative path, 4 is absolute path
app.config['UPLOAD_FOLDER'] = 'static/files'
app.config['SECRET_KEY'] = 'jj8^^83jd)))ueid9ieSHI!!'
db.init_app(app)

FILES_DIRECTORY = './static/files/'

print(os.path.dirname(os.path.abspath(__file__)))

class UploadFileForm(FlaskForm): #FlaskForm module for booking_analysis page
    file = FileField('File', validators=[InputRequired()])
    submit = SubmitField('Upload File')

class LateFine(db.Model): #Creates SQL database model 
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    penn_id = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Integer, default=0, nullable=False)
    booking_number = db.Column(db.String(200), nullable=False)
    details = db.Column(db.String(200), nullable=False)
    schedule = db.Column(db.String(200), nullable=False)
    return_time = db.Column(db.DateTime)
    operator = db.Column(db.String(200), nullable=False)
    date_sent = db.Column(db.DateTime, default=(datetime.now()))
    forgiven = db.Column(db.String(200), nullable=False)
    selected = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return '<Task %r>' % self.id #when you create new element, it returns the task and the id of the task created 

with app.app_context():
    db.create_all()

# def auth_required(f):
#     @wraps(f)
#     #simple HTTP authentication, add @auth_required after each route you want to protect
#     def decorated(*args, **kwargs):
#         auth = request.authorization
#         if auth and auth.username == 'vdmlstaff' and auth.password == 'pythonApp!':
#             return f(*args, **kwargs)

#         return make_response('Invalid login credentials.', 401, {'WWW-Authenticate' : 'Basic realm="Login Required"'})

#     return decorated

selectedSet = set()
sortingParameter = '' #database column name
sortingOrder = '' #asc or desc
searchIDList = []
filteredDate = None
filteredDateHTML = ''
resultUser = ''
resultCirc = ''
generateEmailCount = 1
chartSelection = ''

def searchDatabase(searchTerm):
    global searchIDList
    searchIDList = []
    allEntries = LateFine.query.all()
    for entry in allEntries:
        entryString = ((entry.name + entry.penn_id + entry.email + str(entry.amount) + entry.details + entry.schedule + str(entry.return_time)
         + entry.operator + str(entry.date_sent) + entry.forgiven).lower())
        if searchTerm in entryString:
            searchIDList.append(entry.id)
    return LateFine.query.filter(LateFine.id.in_(searchIDList)).all()

@app.route('/')  #routes to index.html so you don't 404
# @auth_required
def index():
    return render_template('index.html')

@app.route('/booking_analysis', methods=['POST', 'GET'])
# @auth_required
def booking_analysis():
    global chartSelection
    form = UploadFileForm()
    filename = ''

    if form.validate_on_submit():
        try:
            file = form.file.data
            file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'], secure_filename(file.filename)))
            filename = file.filename
            filename = filename.replace(' ', '_')
            filename = filename.replace('(', '')
            filename = filename.replace(')', '')
            (equipmentList, countList, dayList, popularDayCount, hourList, hourCountList, dayHour, dayHourCount, 
            categoryList, categoryCount, noShowUsername, noShowCount, timeDifferenceList, timeDifferenceCount, sortedPopularUsers, 
            numberEquipment, numberUniqueBookings, lateReturnNames, lateReturnMinutes) = bookingAnalysis.analyzeCSV(filename)

            return render_template('booking_analysis_chart.html', form=form, equipmentList = json.dumps(equipmentList), countList = json.dumps(countList),
                dayList = json.dumps(dayList), popularDayCount = json.dumps(popularDayCount), hourList = json.dumps(hourList),
                hourCountList = json.dumps(hourCountList), dayHour = json.dumps(dayHour), dayHourCount = json.dumps(dayHourCount), categoryList = json.dumps(categoryList),
                categoryCount = json.dumps(categoryCount), noShowUsername = json.dumps(noShowUsername), noShowCount = json.dumps(noShowCount),
                timeDifferenceList = json.dumps(timeDifferenceList), timeDifferenceCount = json.dumps(timeDifferenceCount), sortedPopularUsers = json.dumps(sortedPopularUsers),
                numberEquipment = json.dumps(numberEquipment), numberUniqueBookings = json.dumps(numberUniqueBookings), lateReturnNames = json.dumps(lateReturnNames),
                lateReturnMinutes = json.dumps(lateReturnMinutes), equipmentListLength = len(equipmentList), timeDifferenceLength = len(timeDifferenceList),
                popularUsersLength = len(sortedPopularUsers), lateReturnLength = len(lateReturnNames), chartSelection = chartSelection)
        except:
            flash('Invalid file format or file name. Make sure the CSV was not edited in another program and there are no special characters in the filename.')
            return render_template('booking_analysis.html', form=form)

    return render_template('booking_analysis.html', form=form)

@app.route('/download-analysis', methods=['GET'])
# @auth_required
def download_analysis():
    downloadPath = os.path.join(os.path.dirname(__file__), app.config['UPLOAD_FOLDER'])
    excelFilename = 'bookingAnalysis.xlsx'
    return send_from_directory(downloadPath, excelFilename)

@app.route("/late_equipment", methods=['POST', 'GET'])
# @auth_required
def late_equipment(visibility='hidden'):
    if request.method == 'POST':
        text = request.form['text']
        processed_text = ''
        try:
            processed_text = lateEquipment.generateEmail(text)
        except:
            processed_text = 'Failed to extract data.'
        subjectLine = 'Vitale Digital Media Lab - Late Equipment'
        userEmail = request.form['email']
        return redirect(f'mailto:{userEmail}?Subject={subjectLine}&body={processed_text}')
        #return render_template('late_equipment.html', originalText=text, resultText=processed_text, methods=['POST'], visibility='visible')
    else:
        return render_template('late_equipment.html', visibility='hidden')

@app.route("/late_fines", methods=['POST', 'GET'])
# @auth_required
def late_fines(visibility='hidden', cols='0', resulTextCSV=None, visibilityCSV='hidden', visibilityUser='hidden', visbilityCirc='hidden'):
    currentDB = LateFine.query.all()
    global searchIDList
    global filteredDate 
    global filteredDateHTML
    global resultUser
    global resultCirc
    global generateEmailCount

    for entry in currentDB:
        if entry.selected:
            selectedSet.add(entry.id)



    form = UploadFileForm()
    filename = ''

    # CSV UPLOAD
    if form.validate_on_submit():
        # try:
        file = form.file.data
        file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'], secure_filename(file.filename)))
        filename = file.filename
        filename = filename.replace(' ', '_')
        filename = filename.replace('(', '')
        filename = filename.replace(')', '')
        #os.chdir(FILES_DIRECTORY)

        filename = FILES_DIRECTORY + filename
        print(filename)

        with open(filename, 'r') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter='\t')
            i = 0
            for row in csv_reader:
                if i > 0:
                    owner, pennID, email, amount, bookingNum, equipmentString, dateRange, returnTime, staffName, dateUpdate, forgiven, selected = row
                    amount = int(amount)
                    returnTime = datetime.strptime(returnTime, '%Y-%m-%d %H:%M:%S')
                    dateUpdate = datetime.strptime(dateUpdate, '%Y-%m-%d %H:%M:%S')
                    new_entry = LateFine(name=owner, penn_id=pennID, email=email, amount=amount, booking_number=bookingNum, 
                        details=equipmentString, schedule=dateRange, return_time=returnTime, operator=staffName, date_sent=dateUpdate, forgiven=forgiven)
                    db.session.add(new_entry)
                    db.session.commit()
                i += 1
            csv_file.close()

        os.remove(filename)

        return redirect('/late_fines')

        # except Exception as e:
        #     flash('Invalid CSV formatting. Make sure the "Return", "Date Added" and "Amount" columns follow the required format exactly and that there are no special characters in the filename.')
        #     return redirect('/late_fines')

    if request.method == 'POST':
        if 'add-entry' in request.form:
            text = request.form['text']
            owner, bookingNum, equipmentString, dateRange, returnTime, staffName, todayDate = ['', '', '', '', datetime(1900, 1, 1, 0), '', '']
            try:
                if not text == '':
                    owner, bookingNum, equipmentString, dateRange, returnTime, staffName, todayDate = lateFinesCsv.generateCSV(text)
                    returnTime = datetime.strptime(returnTime, '%m/%d/%Y %I:%M %p')
            except Exception as e:
                print(e)
                flash('Error: The script failed to extract data from pasted text. Blank fields added.')

            pennID = request.form['penn-id']
            email = request.form['user-email']
            amount = request.form['fine-amount']
            forgiven = request.form['forgiven']
            dateSent = datetime.now()
            dateUpdate = dateSent.replace(hour=0, minute=0, second=0, microsecond=0)
            new_entry = LateFine(name=owner, penn_id=pennID, email=email, amount=amount, booking_number=bookingNum, 
                details=equipmentString, schedule=dateRange, return_time=returnTime, operator=staffName, date_sent=dateUpdate, forgiven=forgiven)
            db.session.add(new_entry)
            db.session.commit()
            return redirect('/late_fines')
        
        elif 'update-entry' in request.form:
            idToUpdate = request.form['id-to-update']
            lateFine = LateFine.query.get_or_404(idToUpdate)
            lateFine.name = request.form['name']
            lateFine.penn_id = request.form['penn-id']
            lateFine.email = request.form['email']
            lateFine.amount = request.form['amount']
            lateFine.booking_number = request.form['booking_number']
            lateFine.details = request.form['details']
            lateFine.schedule = request.form['schedule']
            # date format = 2018-06-07T00:00
            if request.form['return_time']:
                lateFine.return_time = datetime.strptime(request.form['return_time'], '%Y-%m-%dT%H:%M')
            else:
                lateFine.return_time = datetime.strptime('1900-01-01T00:00', '%Y-%m-%dT%H:%M')
            lateFine.operator = request.form['operator']
            lateFine.date_sent = datetime.strptime(request.form['date_sent'], '%Y-%m-%d')
            lateFine.forgiven = request.form['forgiven']
            db.session.commit()
            return redirect('/late_fines')
        elif 'download-csv' in request.form:
            tasks = LateFine.query.all()
            os.chdir(FILES_DIRECTORY)

            with open('lateFines.csv', 'w', newline='') as csv_file:
                csv_writer = csv.writer(csv_file, delimiter='\t')
                csv_writer.writerow(['Name', 'Penn ID', 'Email', 'Amount', 'Booking', 'Details', 'Schedule', 'Return', 'Operator', 'Date Added', 'Notes', 'Selected'])
                for task in tasks:
                    if task.selected:
                        csv_writer.writerow([task.name, task.penn_id, task.email, task.amount, task.booking_number, 
                            task.details, task.schedule, task.return_time, task.operator, task.date_sent, task.forgiven, task.selected])
                csv_file.close()

            downloadPath = os.path.join(os.path.dirname(__file__), app.config['UPLOAD_FOLDER'])
            csvFilename = 'lateFines.csv'
            return send_from_directory(downloadPath, csvFilename)
        elif 'generate-emails' in request.form:
            generateEmailCount = 0
            tasks = LateFine.query.order_by(LateFine.date_sent).all()
            resultUser = ''
            if selectedSet:
                resultCirc = SEPARATOR
                for id in selectedSet:
                    currentEntry = LateFine.query.get_or_404(id)
                    resultUser += SEPARATOR + lateFinesUserEmail.generateEmail(currentEntry.name, currentEntry.amount, currentEntry.details, 
                        currentEntry.schedule, currentEntry.return_time) + '\n\n'
                    resultCirc += f'''{currentEntry.name}\n{currentEntry.penn_id}\n{currentEntry.email}\n${currentEntry.amount}\n{currentEntry.booking_number}\n{currentEntry.details}\n\n-----------------------------------------\n'''
                resultUser += SEPARATOR
            else:
                resultCirc = ''
            return redirect('/late_fines')

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
            global filteredDate
            global filteredDateHTML
            dateAdded = request.form['added-date']
            try:
                filteredDate = datetime.strptime(dateAdded, '%Y-%m-%d')
                filteredDateHTML = datetime.strftime(filteredDate, '%Y-%m-%d')
            except ValueError:
                print(ValueError)
            tasks = LateFine.query.filter_by(date_sent=filteredDate).all()
            return render_template('late_fines.html', form=form, tasks=tasks, cols='0', visibility='hidden', filteredDate=filteredDateHTML, visibilityCSV='hidden', visibilityUser='hidden', visibilityCirc='hidden')
        elif 'clear-filters' in request.form:
            searchIDList = []
            filteredDate = None
            tasks = LateFine.query.all()
            return render_template('late_fines.html', form=form, tasks=tasks, cols='0', visibility='hidden', visibilityCSV='hidden', visibilityUser='hidden', visibilityCirc='hidden')
        elif 'search' in request.form:
            searchTerm = request.form['search'].lower()
            tasks = searchDatabase(searchTerm)
            return render_template('late_fines.html', form=form, tasks=tasks, cols='0', visibility='hidden', visibilityCSV='hidden', visibilityUser='hidden', visibilityCirc='hidden')

    else:
        if len(searchIDList) > 0:
            tasks = LateFine.query.filter(LateFine.id.in_(searchIDList)).all()
        elif sortingParameter and filteredDate:
            if sortingParameter == 'name' and sortingOrder == 'desc':
                tasks = LateFine.query.order_by(LateFine.name.desc()).filter_by(date_sent=filteredDate).all() 
            elif sortingParameter == 'name' and sortingOrder == 'asc':
                tasks = LateFine.query.order_by(LateFine.name.asc()).filter_by(date_sent=filteredDate).all()
            elif sortingParameter == 'email' and sortingOrder == 'desc':
                tasks = LateFine.query.order_by(LateFine.email.desc()).filter_by(date_sent=filteredDate).all()
            elif sortingParameter == 'email' and sortingOrder == 'asc':
                tasks = LateFine.query.order_by(LateFine.email.asc()).filter_by(date_sent=filteredDate).all()
            elif sortingParameter == 'amount' and sortingOrder == 'desc':
                tasks = LateFine.query.order_by(LateFine.amount.desc()).filter_by(date_sent=filteredDate).all()
            elif sortingParameter == 'amount' and sortingOrder =='asc':
                tasks = LateFine.query.order_by(LateFine.amount.asc()).filter_by(date_sent=filteredDate).all()
            elif sortingParameter == 'booking' and sortingOrder == 'desc':
                tasks = LateFine.query.order_by(LateFine.booking_number.desc()).filter_by(date_sent=filteredDate).all()
            elif sortingParameter == 'booking' and sortingOrder =='asc':
                tasks = LateFine.query.order_by(LateFine.booking_number.asc()).filter_by(date_sent=filteredDate).all()
            elif sortingParameter == 'return_time' and sortingOrder == 'desc':
                tasks = LateFine.query.order_by(LateFine.return_time.desc()).filter_by(date_sent=filteredDate).all()
            elif sortingParameter == 'return_time' and sortingOrder == 'asc':
                tasks = LateFine.query.order_by(LateFine.return_time.asc()).filter_by(date_sent=filteredDate).all()
            elif sortingParameter == 'operator' and sortingOrder == 'desc':
                tasks = LateFine.query.order_by(LateFine.operator.desc()).filter_by(date_sent=filteredDate).all()
            elif sortingParameter == 'operator' and sortingOrder == 'asc':
                tasks = LateFine.query.order_by(LateFine.operator.asc()).filter_by(date_sent=filteredDate).all()
            elif sortingParameter == 'date_sent' and sortingOrder == 'desc':
                tasks = LateFine.query.order_by(LateFine.date_sent.desc()).filter_by(date_sent=filteredDate).all()
            elif sortingParameter == 'date_sent' and sortingOrder == 'asc':
                tasks = LateFine.query.order_by(LateFine.date_sent.asc()).filter_by(date_sent=filteredDate).all()
        elif sortingParameter and not filteredDate:
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

        elif filteredDate:
            tasks = LateFine.query.filter_by(date_sent=filteredDate).all()
        else:
            tasks = LateFine.query.order_by(LateFine.date_sent).all()

        if generateEmailCount == 0:
            generateEmailCount += 1
            return render_template('late_fines.html', form=form, methods=['POST'], resultTextCirc=resultCirc, resultTextUser=resultUser,
                visibilityCSV='hidden', visibilityCirc='visible', tasks=tasks)
        try:
            return render_template('late_fines.html', form=form, filteredDate=filteredDate, tasks=tasks, cols='0', visibility='hidden', visibilityCSV='hidden', visibilityUser='hidden', visibilityCirc='hidden')
        except:
            tasks = LateFine.query.order_by(LateFine.date_sent).all()
            return render_template('late_fines.html', form=form, tasks=tasks, cols='0', visibility='hidden', visibilityCSV='hidden', visibilityUser='hidden', visibilityCirc='hidden')
  
@app.route('/sort-desc-name')
def sortDescName():
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
    sortingParameter = 'booking'
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
    return redirect('/late_fines')

@app.route('/generateUserEmail/<int:id>')
def generateUserEmail(id):
    currentEntry = LateFine.query.get_or_404(id)
    subjectLine = 'Vitale Digital Media Lab - Late Fine'
    userEmail = currentEntry.email
    resultUser = lateFinesUserEmail.generateEmail(currentEntry.name, currentEntry.amount, currentEntry.details, currentEntry.schedule, currentEntry.return_time)
    return redirect(f'mailto:{userEmail}?Subject={subjectLine}&body={resultUser}')

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

if __name__ == "__main__": # watches for changes and updates
    app.run(port=8000, debug=True)