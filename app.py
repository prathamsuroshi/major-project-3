#importing libraries
from extract_txt import read_files
from txt_processing import preprocess
from txt_to_features import txt_features, feats_reduce
from extract_entities import get_number, get_email, rm_email, rm_number, get_name, get_skills
from model import simil
import pandas as pd
import json
import os
import nltk
from nltk.tokenize import sent_tokenize
nltk.download('averaged_perceptron_tagger')
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.tag import pos_tag
nltk.download('wordnet')
nltk.download('omw-1.4')
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.tag import pos_tag
from nltk.corpus import wordnet 
from flask import session
# from flask_cachebuster import CacheBuster

# app = Flask(__name__)
# cachebuster = CacheBuster(config={'extensions': ['.js', '.css'], 'hash_size': 5})
# cachebuster.init_app(app)


# Download the 'punkt' resource
nltk.download('punkt')

import uuid
from flask import Flask, flash, request, redirect, url_for, render_template, send_file

#used directories for data, downloading and uploading files 
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'files/resumes/')
DOWNLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'files/outputs/')
DATA_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Data/')

# Make directory if UPLOAD_FOLDER does not exist
if not os.path.isdir(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)

# Make directory if DOWNLOAD_FOLDER does not exist
if not os.path.isdir(DOWNLOAD_FOLDER):
    os.mkdir(DOWNLOAD_FOLDER)
#Flask app config 
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER
app.config['DATA_FOLDER'] = DATA_FOLDER
app.config['SECRET_KEY'] = 'nani?!'
# cachebuster = CacheBuster(config={'extensions': ['.js', '.css'], 'hash_size': 5})
# cachebuster.init_app(app)
# Allowed extension you can set your own
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'doc','docx'])

# Global variable to track app state
app_initialized = False

def reset_app():
    # Clear uploaded files
    for file in os.listdir(app.config['UPLOAD_FOLDER']):
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            flash(f'Error deleting file {file}: {str(e)}')

    # Clear ranking file
    ranking_file = os.path.join(app.config['DOWNLOAD_FOLDER'], 'Candidates.csv')
    if os.path.exists(ranking_file):
        try:
            os.remove(ranking_file)
        except Exception as e:
            flash(f'Error deleting ranking file: {str(e)}')


    # Clear generated CSV files
    generated_csv_files = [f for f in os.listdir(app.config['DOWNLOAD_FOLDER']) if f.endswith('.csv')]
    for csv_file in generated_csv_files:
        csv_file_path = os.path.join(app.config['DOWNLOAD_FOLDER'], csv_file)
        try:
            if os.path.isfile(csv_file_path):
                os.unlink(csv_file_path)
        except Exception as e:
            flash(f'Error deleting CSV file {csv_file}: {str(e)}')
            
    # Clear Jinja cache
    app.jinja_env.cache = {}

    # Clear session data
    session.clear()

    # Set the app state to initialized
    global app_initialized
    app_initialized = True

    flash('App reset successfully')
    return redirect(url_for('main_page'))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
 
@app.route('/', methods=['GET'])
def main_page():
    global app_initialized
    reset_requested = request.args.get('reset', False)

    if reset_requested:
        return reset_app()  # Call the reset_app function if reset is requested
    elif not app_initialized:
        remove_all_files()
        app_initialized = True
        # Perform additional actions for the initial state, if needed
        pass

    return _show_page()
 
@app.route('/', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    app.logger.info(request.files)
    upload_files = request.files.getlist('file')
    app.logger.info(upload_files)
    # If the user does not select a file, the browser submits an
    # empty file without a filename.
    if not upload_files:
        flash('No selected file')
        return redirect(request.url)
    for file in upload_files:
        original_filename = file.filename
        if allowed_file(original_filename):
            extension = original_filename.rsplit('.', 1)[1].lower()
            filename = str(uuid.uuid1()) + '.' + extension
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            file_list = os.path.join(UPLOAD_FOLDER, 'files.json')
            files = _get_files()
            files[filename] = original_filename
            with open(file_list, 'w') as fh:
                json.dump(files, fh)
 
    flash('Upload succeeded')
    # return redirect(url_for('upload_file'))
    return redirect(url_for('main_page'))

 
 
@app.route('/download/<code>', methods=['GET'])
def download(code):
    files = _get_files()
    if code in files:
        path = os.path.join(UPLOAD_FOLDER, code)
        if os.path.exists(path):
            return send_file(path)
    # abort(404)
 
# def _show_page():
#     files = _get_files()
#     return render_template('index.html', files=files)
 
def _get_files():
    file_list = os.path.join(UPLOAD_FOLDER, 'files.json')
    if os.path.exists(file_list):
        with open(file_list) as fh:
            return json.load(fh)
    return {}

@app.route('/remove/<filename>', methods=['GET'])
def remove_file(filename):
    try:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        # Remove the file from the filesystem
        if os.path.exists(file_path):
            os.remove(file_path)

            # Update the files.json to remove the entry
            files = _get_files()
            if filename in files:
                del files[filename]
                with open(os.path.join(app.config['UPLOAD_FOLDER'], 'files.json'), 'w') as fh:
                    json.dump(files, fh)

            flash('File removed successfully')
        else:
            flash('File not found')
    except Exception as e:
        flash(f'Error: {str(e)}')

    return redirect(url_for('main_page'))


# ... (your existing Flask code)

@app.route('/remove_all_files', methods=['POST'])
def remove_all_files():
    try:
        # Clear uploaded files
        for file in os.listdir(app.config['UPLOAD_FOLDER']):
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                flash(f'Error deleting file {file}: {str(e)}')

        # Clear ranking file
        ranking_file = os.path.join(app.config['DOWNLOAD_FOLDER'], 'Candidates.csv')
        if os.path.exists(ranking_file):
            try:
                os.remove(ranking_file)
            except Exception as e:
                flash(f'Error deleting ranking file: {str(e)}')

        # Clear generated CSV files
        generated_csv_files = [f for f in os.listdir(app.config['DOWNLOAD_FOLDER']) if f.endswith('.csv')]
        for csv_file in generated_csv_files:
            csv_file_path = os.path.join(app.config['DOWNLOAD_FOLDER'], csv_file)
            try:
                if os.path.isfile(csv_file_path):
                    os.unlink(csv_file_path)
            except Exception as e:
                flash(f'Error deleting CSV file {csv_file}: {str(e)}')

        flash('All files cleared successfully')
    except Exception as e:
        flash(f'Error: {str(e)}')

    return redirect(url_for('main_page'))

# ... (your existing Flask code)


@app.route('/process',methods=["POST","GET"])
def process():
    if request.method == 'POST':

        out_path = os.path.join(DOWNLOAD_FOLDER, 'Candidates.csv')
        if os.path.exists(out_path):
            os.remove(out_path)
        
        rawtext = request.form['rawtext']
        jdtxt=[rawtext]
        resumetxt=read_files(UPLOAD_FOLDER)
        p_resumetxt = preprocess(resumetxt)
        p_jdtxt = preprocess(jdtxt)

        feats = txt_features(p_resumetxt, p_jdtxt)
        feats_red = feats_reduce(feats)

        df = simil(feats_red, p_resumetxt, p_jdtxt)
        if feats_red is not None and not feats_red.empty:
            t = pd.DataFrame({'Original Resume':resumetxt})
            dt = pd.concat([df,t],axis=1)

            dt['Phone No.']=dt['Original Resume'].apply(lambda x: get_number(x))
            
            dt['E-Mail ID']=dt['Original Resume'].apply(lambda x: get_email(x))
            #new code
            dt['CGPA'] = dt['Original Resume'].apply(lambda x: get_number(x, cgpa=True))
            dt['CGPA'] = dt['CGPA'].apply(lambda x: x if x is not None else 'Not Found')

            dt['Original']=dt['Original Resume'].apply(lambda x: rm_number(x))
            dt['Original']=dt['Original'].apply(lambda x: rm_email(x))
            dt['Candidates Name']=dt['Original'].apply(lambda x: get_name(x))

            skills = pd.read_csv(DATA_FOLDER+'skill_red.csv')
            skills = skills.values.flatten().tolist()
            skill = []
            for z in skills:
                r = z.lower()
                skill.append(r)

            dt['Skills']=dt['Original'].apply(lambda x: get_skills(x,skill))
            dt = dt.drop(columns=['Original','Original Resume'])
            if 'JD 1' in dt.columns:
                sorted_dt = dt.sort_values(by=['JD 1'], ascending=False)

                out_path = DOWNLOAD_FOLDER +'Candidates.csv'
                sorted_dt[['Candidates Name', 'Phone No.', 'E-Mail ID', 'Skills']].to_csv(out_path, index=False)
                # sorted_dt.to_csv(out_path,index=False)
                
                ranking_df =pd.read_csv(out_path)
                ranking = list(zip(ranking_df.index + 1, ranking_df['Candidates Name'].tolist()))

                return render_template('index.html',files = _get_files(),ranking = ranking)
            else:
                    flash("Error: 'JD 1' column not found.")
                    return render_template('index.html', files=_get_files())
            
        else:
            flash("Error: Feats DataFrame is None or empty.")
            return render_template('index.html', files=_get_files())
        
    # if request.method == 'GET':
    #     out_path = DOWNLOAD_FOLDER + 'Candidates.csv'
    #     return send_file(out_path, as_attachment=True)
    if request.method == 'GET':
        out_path = DOWNLOAD_FOLDER + 'Candidates.csv'
        if os.path.exists(out_path):
            ranking_df = pd.read_csv(out_path)
            if 'JD 1' not in ranking_df.columns:
                remove_all_files()
                # If 'JD 1' column is not present, redirect to the main page
                return redirect(url_for('main_page'))

            return send_file(out_path, as_attachment=True)
        else:
            return redirect(url_for('main_page'))

# ... (your existing Flask code)

def _show_page():
    files = _get_files()

    if not app_initialized:
        # Perform additional actions for the initial state, if needed
        pass

    session.clear()
    
    # app.jinja_env.cache = {}
    if files:
        # Add the following to get ranking information
        ranking_file = os.path.join(app.config['DOWNLOAD_FOLDER'], 'Candidates.csv')
        if os.path.exists(ranking_file):
            ranking_df = pd.read_csv(ranking_file)
            # new code
            if 'JD 1' not in ranking_df.columns:
                flash("Error: 'JD 1' column not found.")
                return render_template('index.html', files=files)
            # new code end
            ranking = list(zip(ranking_df.index + 1, ranking_df['JD 1'].tolist()))
        else:
            ranking = []

        return render_template('index.html', files=files, ranking=ranking)
    else:
        return render_template('index.html', files=files)

if __name__=="__main__":
    app.run(port=8080, debug=False)
