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
model = keras.models.load_model('facemaskcnn.h5')

from tempfile import NamedTemporaryFile

st.set_option('deprecation.showfileUploaderEncoding', False)






#@st.cache(allow_output_mutation=True)
def highlight_faces(model,image):
    from mtcnn.mtcnn import MTCNN
    import cv2
    from matplotlib.patches import Rectangle

    #@st.cache(allow_output_mutation=True)
    def detect_faces(image):
        im = np.asarray(image)
        im= np.array(im)[...,:3]
        detector = MTCNN()
        #img = cv2.resize(im,(240,240))     # resize image to match model's expected sizing
        #img = img.reshape(1,240,240,3)
        faces = detector.detect_faces(im)
        return faces

    # for each face, draw a rectangle based on coordinates
    #@st.cache(allow_output_mutation=True)
    def get_predictions(faces):
        facepredictions,facelist=[],[]
        for face in faces:
            x, y, width, height = face['box']
            im = image
            im = im.crop((x-10,y-10,x+width+20,y+height+20))
            imresized = im.resize((32,32))
            imarray=np.array(imresized)[...,:3]
            facelist.append(imarray)
            facepredictions.append(dict(x=x,y=y,width=width,height=height))
        facearray=np.stack([np.array(im)[...,:3]  for im in facelist], axis=0)
        #facearray=np.stack([im for im in facelist], axis=0)

        st.write(f'{len(facelist)} faces were found')
        predictions = model.predict(facearray/255)
        #st.write('predictions shape',predictions.shape)
        predictions=np.argmax(predictions,axis=1)
        #st.write(predictions)
        for i,face in enumerate(facepredictions):
            facepredictions[i]['prediction'] = predictions[i]
                    
        return facepredictions
    #@st.cache(allow_output_mutation=True)
    def mark_faces(**fp):
        #Color code for classes
        colors={0:'orange',1:'green',2:'red'}
        #Mark face borders
        face_border = Rectangle((fp['x']-5, fp['y']-5), fp['width']+10, fp['height']+10,
                          fill=False, color=colors[fp['prediction']])
        ax.add_patch(face_border)
    #End embedded functions
    #Main function code
    faces=detect_faces(image)    
    # display base image
    #img = plt.imread(image)
    img = plt.imshow(image)

    ax = plt.gca()
    # Get predictions
    predictions=get_predictions(faces)
    
    # Mark faces by prediction
    for pred in predictions:
        mark_faces(**pred)
    return plt


def main():

    st.header("Face Mask Detection")
    st.subheader("Drag and drop an image with faces.")
    st.markdown("""<p>Face mask classification:</p><span style="color:green;">Correctly worn mask |</span> <span style="color:orange;"> Incorrectly worn mask |</span><span style="color:red;"> Without mask</span>""",unsafe_allow_html=True)
    buffer = st.file_uploader("Upload Image",type=['png','jpeg','jpg'])
    temp_file = NamedTemporaryFile(delete=False)
    if buffer:
        temp_file.write(buffer.getvalue())
        #st.write(load_img(temp_file.name))
        #st.write(temp_file.name)        
        image = Image.open(temp_file.name)
        #st.image(image, caption='test image')
        st.pyplot(highlight_faces(model,image))

if __name__ == "__main__":
    main()