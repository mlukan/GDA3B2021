import streamlit as st
import pandas as pd
import json
import copy
import numpy as np
import seaborn as sns
import base64
from PIL import Image
import io
import os
import keras
import matplotlib.pyplot as plt

# Load local face mask detection model, can be exchanged for a better one :)
model = keras.models.load_model('facemaskcnn.h5')

# How to run this file:
# streamlit run app.py
# on default port, or set the port explicitly such as:
# streamlit run app.py --server.port 8080

from tempfile import NamedTemporaryFile

st.set_option('deprecation.showfileUploaderEncoding', False)

# Cache decorators had to be removed as below,because  streamlit cannot hash keras objects
#@st.cache(allow_output_mutation=True)
def highlight_faces(model,image):
    from mtcnn.mtcnn import MTCNN
    import cv2
    from matplotlib.patches import Rectangle
    
    #---Start embedded functions---
    #@st.cache(allow_output_mutation=True)
    def detect_faces(image):
        im = np.asarray(image)
        im= np.array(im)[...,:3]
        detector = MTCNN()
        #img = cv2.resize(im,(240,240))     # resize image to match model's expected sizing
        #img = img.reshape(1,240,240,3)
        faces = detector.detect_faces(im)
        return faces

    # Get predictions  for all faces in image, return a list of dictionaries with face locations and predictions
    #@st.cache(allow_output_mutation=True)
    def get_predictions(faces):
        facepredictions,facelist=[],[]
        
        # Extract, crop and resize all detected faces
        for face in faces:
            x, y, width, height = face['box']
            im = image
            im = im.crop((x-10,y-10,x+width+20,y+height+20))
            imresized = im.resize((32,32))
            imarray=np.array(imresized)[...,:3]
            facelist.append(imarray)
            # Save face location metadata for later use
            facepredictions.append(dict(x=x,y=y,width=width,height=height))
        
        # Create a numpy array of all faces for model input    
        facearray=np.stack([np.array(im)[...,:3]  for im in facelist], axis=0)
        
        # Write number of faces on the webpage
        st.write(f'{len(facelist)} faces were found')
        # Make face mask prediction on the face numpy array input
        predictions = model.predict(facearray/255)
        #st.write('predictions shape',predictions.shape)
        predictions=np.argmax(predictions,axis=1)
        #st.write(predictions)
        
        #Append prediction data  to the face metadata list
        for i,face in enumerate(facepredictions):
            facepredictions[i]['prediction'] = predictions[i]
        
        #Return list of image location metadata and predictions            
        return facepredictions
    
    # Mark face boundaries on the image and color the rectangles  by prediction
    #@st.cache(allow_output_mutation=True)
    def mark_faces(**fp):
        #Color code for classes
        colors={0:'orange',1:'green',2:'red'}
        #Mark face borders
        face_border = Rectangle((fp['x']-5, fp['y']-5), fp['width']+10, fp['height']+10,
                          fill=False, color=colors[fp['prediction']])
        ax.add_patch(face_border)
    #---end of embedded functions---
    
    #---Start main function code---
    faces=detect_faces(image)    
    
    # Display base image
    img = plt.imshow(image)

    ax = plt.gca()
    # Get predictions
    predictions=get_predictions(faces)
    
    # Plot predicted face boundaries  over the base image
    for pred in predictions:
        mark_faces(**pred)
    
    # Return plot
    return plt


def main():
    # Streamlit header text
    st.header("Face Mask Detection")
    st.subheader("Drag and drop an image with faces.")
    
    # Streamlit embedded html code, just used for color styling
    st.markdown("""<p>Face mask classification:</p><span style="color:green;">Correctly worn mask |</span> <span style="color:orange;"> Incorrectly worn mask |</span><span style="color:red;"> Without mask</span>""",unsafe_allow_html=True)
    
    # File uploader, load image into teporary buffer
    buffer = st.file_uploader("Upload Image",type=['png','jpeg','jpg'])
    temp_file = NamedTemporaryFile(delete=False)
    if buffer:
        temp_file.write(buffer.getvalue())
        # Open the file from the buffer as PIL image
        image = Image.open(temp_file.name)
        
        # Streamlit call to plot the (pyplot) output of the highlight_faces function
        st.pyplot(highlight_faces(model,image))

if __name__ == "__main__":
    main()