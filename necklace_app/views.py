#!/usr/bin/env python3
from flask import render_template, request, url_for
from werkzeug.utils import secure_filename
import os
import urllib.request
import shutil
from flask import send_from_directory, flash, redirect
from necklace_app.front_end_funcs import *
from necklace_app import app

#------------------------------------------------
UPLOAD_FOLDER = '/home/ubuntu/application/necklace_app/static/uploads/'
IMAGE_FOLDER = './static/data/all_images/'
DISPLAY_FOLDER = './static/uploads/'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['IMAGE_FOLDER'] = IMAGE_FOLDER
app.config['DISPLAY_FOLDER'] = DISPLAY_FOLDER
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config.update(
    TESTING=True,
    SECRET_KEY=b'secret_key')

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
@app.route('/input')
def index():
    return render_template("input.html")

@app.route('/uploads/<filename>')
def send_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/results', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'GET':
        return render_template('input.html')

    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            print('No file 1')
            return render_template('input.html')
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            print('No file 2')
            return render_template('input.html')
        if file and allowed_file(file.filename):
            img_file = request.files.get('file')
            img_name = secure_filename(img_file.filename)
            img_path = os.path.join(app.config['UPLOAD_FOLDER'], img_name)
            file.save(img_path)
            
            # Set path to reach downloaded file
            orig_path = os.path.join(app.config['DISPLAY_FOLDER'], img_name)
            
            category, listing_info, distances = return_similar_necklaces(img_path)
            
            if category=='keep': # necklace detected
                
                title = "The necklaces most resembling the one you uploaded:"
                price = "Price is "
                
                # Format listing_info for printing
                files = []
                for e in listing_info['listing_id']:
                    files.append(app.config['IMAGE_FOLDER']+str(e)+".jpg")
                listing_info['file']=files
                
                prices = []
                for p in listing_info['price']:
                    prices.append("${:.2f}".format(p))
                listing_info['price']=prices

                dists = []
                for d in distances[1:]:
                    dists.append("{number:.{digits}f}".format(number=d*100,digits=1)+"% match")
                listing_info['distances']=dists

                listings = listing_info.to_dict('records')


                return render_template('output.html',
                                       listings=listings,
                                       original=orig_path,
                                       title = "Here are the 4 closest necklaces we could find in our database:",
                                       note="Note: Prices fluctuate daily. The price listed below may not be the most up-to-date.")
                
            else:
                title = "Sadly, we did not detect a necklace in your photo."
                price = "Please try again."
                sadimg = './static/data/disappointed-face.png'
                linktext = "Click here to go to Etsy, anyway."
                
                returnval = render_template('output.html', 
                        original=orig_path,
                        category=category, 
                        price1=price, 
                        title = title, 
                        img_rec1=sadimg, 
                        url_rec1 = "https://www.etsy.com/c/jewelry/necklaces?ref=catnav-10855")
        return returnval
            
            
    return render_template('input.html')
    


if __name__ == "__main__":
    app.run(debug=True)
