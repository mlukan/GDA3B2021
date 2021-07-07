# Face mask detection project
Project is based on the [Kaggle face mask competition by andrewmvd](https://www.kaggle.com/andrewmvd/face-mask-detection)  
Dataset contains approximately 850 images with 4072 faces + xml annotations.  
Faces  were extracted using image coordinate metadata, cropped and resized.  
SVM and CNN models were fitted.  
Pretrained face detection (MTCNN) as input for the CNN model  was used in the facemask_detection notebook.  
Small streamlit app for testing on new images was created.  
