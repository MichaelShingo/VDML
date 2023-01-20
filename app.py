from flask import Flask, render_template, flash, request, redirect, url_for
from flask import request
import os
from werkzeug.utils import secure_filename
from scripts import lateEquipment

# virtualenv env 
# source/env/bin/activate
# TODO you might have to install pyperclip in env


UPLOAD_FOLDER = './uploads/'
ALLOWED_EXTENSIONS = {'.csv'}

app = Flask(__name__) #references this file
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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
    return render_template('late_equipment.html', resultText=processed_text, methods=['POST'], visibility='visible')

@app.route("/late_fines")
def late_fines(visibility='hidden', cols='0'):
    return render_template('late_fines.html', cols='0', visibility='hidden')



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