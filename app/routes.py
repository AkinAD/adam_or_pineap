from flask import render_template, flash, redirect, url_for,Flask, request, Response
from werkzeug.utils import secure_filename
from app import app
from app.forms import akinsDataForm
from PIL import Image
import os, sys, requests, time
from io import BytesIO
import tensorflow as tf
from tensorflow.python.keras.backend import set_session
from imageai.Prediction.Custom import CustomImagePrediction

response = Response()
execution_path = os.getcwd()
sesh = tf.Session() #Set these because deploying on Flask uses multithreading or somethin, but setting session and graph at the
#beginning forces the same model , session and graph to be used accross all instances
# whatever this github repo says  : https://github.com/tensorflow/tensorflow/issues/28287#issuecomment-495005162 
graph = tf.get_default_graph()

# def load_model():
global model
set_session(sesh) # set session again
model = CustomImagePrediction()
model.setModelTypeAsResNet()
model.setModelPath("prediction_model.h5") #Load the model -Akns model
model.setJsonPath("prediction_model.json") # and this json for some reason - Akns Json
model.loadModel(num_objects=3) 

global filename 

@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def index(): # could have it so that if they happen to upload two imahges then two image results are shown?
    global form
    form = akinsDataForm()
    if form.validate_on_submit(): # on submit 
        # do some testing
        print("HELLOOOOOOOOOOOOOOOOOOOOOO")
        # flash('UPLOAD Image name should show up here: {}'.format(form.upload.data.filename))
        # flash('URL Image name should show up here: {}'.format(form.url.data))
        # print('UPLOAD Image name should show up here: {}'.format(form.upload.data.filename))
        print('URL Image name should show up here: {}'.format(form.url.data))

        if form.url.data is None or form.upload.data is not None:
            print("in here - A")
            img = secure_filename(form.upload.data.filename)
            # try below 
            # f = form.photo.data
            # filename = secure_filename(f.filename)
            # f.save(os.path.join(
            # app.instance_path, 'photos', filename
            # ))
            return upload_image() # or something
        elif form.url.data is not None or form.upload.data is None :
            print("in here - B")
            url = form.url.data
            response = requests.get(url)
            img = Image.open(BytesIO(response.content))
            global filename
            filename = 'formImage.jpg'
            return predict(img) # or something
    print("Continuing as if no input")
    print("Errors? {}".format(form.errors))
    return render_template('adam.html', title='Adam or Pineapple?', form = form )

# https://stackoverflow.com/questions/46785507/python-flask-display-image-on-a-html-page

def predict(daImage='pinapple.jpg'):
    img = daImage
    rgb_im = img.convert('RGB')
    rgb_im.save('formImage.jpg')
    rgb_im.save('app/static/uploads/formImage.jpg') # i sure do love duplicate code
    filename = "formImage.jpg"
    output = ""
    global sesh, graph
    with graph.as_default(): #uses default graph ( graph from loaded model)
        set_session(sesh) #set session
        predictions, probabilities = model.predictImage('formImage.jpg', result_count=3)
    for eachPrediction, eachProbability in zip(predictions, probabilities):
        # print(eachPrediction , " : " , eachProbability)
        output += eachPrediction + " : " + str(eachProbability) +"% \n"
    print(output)
    flash("Complete! Scroll down to see your results ")
    return render_template('adam.html', title='Results', output = output, user_image='static/formImage.jpg', form = form, filename = filename)

#to use this endpoin -->  $ curl -F "image=@image.jpg" http://localhost:5000/predict
@app.route('/predict', methods=['POST'])
def do_Prediction():
    output = ""
    img = Image.open(request.files['image'])
    # save a image using extension 
    rgb_im = img.convert('RGB')
    rgb_im.save('image.jpg')

    global sesh
    global graph
    with graph.as_default(): #uses default graph ( graph from loaded model)
        set_session(sesh) #set session
        predictions, probabilities = model.predictImage("image.jpg", result_count=3)
    for eachPrediction, eachProbability in zip(predictions, probabilities):
        # print(eachPrediction , " : " , eachProbability)
        output += eachPrediction + " : " + str(eachProbability) +"\n"
    return output

@app.route('/display/<filename>')
def display_image(filename):
	#print('display_image filename: ' + filename)
	return redirect(url_for('static', filename='uploads/' + filename), code=301)

# === consider moving these to a utility class === 

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def upload_image():
    global filename
    print('Request method AFTER calling upload handler {}'.format(request.method))
    print('Contents of request.files AFTER calling upload handler :  {}'.format(request.files))

    if 'upload' not in request.files:
        flash('No upload part')
        print('Upload ERR = No upload part')
        return redirect(request.url)
    file = request.files['upload']
    if file.filename == '':
        flash('No image selected for uploading')
        print('Upload ERR = No image selected for uploading')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        img = Image.open(file)
        #print('upload_image filename: ' + filename)
        flash('Image successfully uploaded and displayed')
        print('Upload ERR = Image successfully uploaded and displayed')
        return predict(img)
    else:
        flash('Allowed image types are -> png, jpg, jpeg')
        return redirec(request.url)

#prevent Caching
@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    # response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'no-cache, no-store'
    return response

#not sure if i need this tbh, setting port and ip 
if __name__ == '__main__':
    # load_model() #load model at the beginning once only 
    # app.run(host='0.0.0.0', port=5000) #this would be 'localhost'
    app.run(host='0.0.0.0', port=80)  #this doesn't work when you use $ flask run 
    # so use $ flask run -h localhost -p 80  -- 80 being the port