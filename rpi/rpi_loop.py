# from emotion model
from imutils.video import VideoStream
import imutils 
import cv2
import time
import numpy as np 
from keras.models import load_model

# from google cloud
from google.cloud import pubsub_v1
import json
import base64

######################
#    Setup Model     #
######################

#video_capture = VideoStream(src=0).start()
#video_capture = cv2.VideoCapture(0)
#target_emotions = ['neutral', 'happiness', 'sad']

# use the rpi camera
video_capture = VideoStream(usePiCamera=True).start()

# load the model
model = load_model('./models/_mini_XCEPTION.102-0.66.hdf5')
model.get_config()
target = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral']
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

time.sleep(2.0)


######################
#    Setup GCloud    #
######################

project_id = "ai-dj-36"
topic_name = "emotion"

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(project_id, topic_name)

# create topic if not exists
project_path = publisher.project_path(project_id)
topics = publisher.list_topics(project_path)
topic_names = [topic.name for topic in topics]
if topic_path not in topic_names:
   topic = publisher.create_topic(topic_path)
   print('Topic created: {}'.format(topic))
        
######################
#     Video loop     #
######################

while True:
    ret, frame = video_capture.read()
    frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(frame_gray, scaleFactor=1.1)

    # iterate through all detected facess
    emotion_results = []
    for (x,y,w,h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2, 5)
        face_crop = frame[y:y + h, x:x + w]
        face_crop = cv2.resize(face_crop, (64, 64))
        face_crop = cv2.cvtColor(face_crop, cv2.COLOR_BGR2GRAY)
        face_crop = face_crop.astype('float32') / 255
        face_crop = np.asarray(face_crop)
        face_crop = face_crop.reshape(1,face_crop.shape[0], face_crop.shape[1],1)
        emotion_result = target[np.argmax(model.predict(face_crop))]
        emotion_results.append(emotion_result)

    # encode the result as a payload
    payload = {"emotions": emotion_results}
    payload = json.dumps(payload)
    payload = payload.encode("utf-8")
        
    # publish it to gcloud
    print(emotion_result)
    future = publisher.publish(topic_path, data=payload)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
video_capture.release()
cv2.destroyALlWindows()
