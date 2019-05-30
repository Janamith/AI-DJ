from imutils.video import VideoStream
import imutils 
import cv2
import time
import numpy as np 
from keras.models import load_model

from playmusic import change_music

#vs = VideoStream(src=0).start()
video_capture = cv2.VideoCapture(0)
#vs = VideoStream(usePiCamera=True).start()
time.sleep(1.0)

target_emotions = ['neutral', 'happiness', 'sad']
model = load_model('./models/_mini_XCEPTION.102-0.66.hdf5')
model.get_config()

emotion_results = []
start_time = time.time()
previous_emotion = 'none'
        
target = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral']
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
while True:
	ret, frame = video_capture.read()
	frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	faces = face_cascade.detectMultiScale(frame_gray, scaleFactor=1.1)
	for (x,y,w,h) in faces:
		cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2, 5)
		face_crop = frame[y:y + h, x:x + w]
		face_crop = cv2.resize(face_crop, (64, 64))
		face_crop = cv2.cvtColor(face_crop, cv2.COLOR_BGR2GRAY)
		face_crop = face_crop.astype('float32') / 255
		face_crop = np.asarray(face_crop)
		face_crop = face_crop.reshape(1,face_crop.shape[0], face_crop.shape[1],1)
		result = target[np.argmax(model.predict(face_crop))]
                
		emotion_results.append(result)
		print(result)
		cv2.putText(frame, result, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (200, 0, 0), 3, cv2.LINE_AA)

	if (time.time() - start_time >= 10 and emotion_results):
                dominant_emotion = max(emotion_results, key=emotion_results.count)
                change_music(dominant_emotion, previous_emotion)
                print("dominant emotion:", dominant_emotion)
                
                start_time = time.time()
                emotion_results = []
                previous_emotion = dominant_emotion
                
	cv2.imshow('frame', frame)
	if cv2.waitKey(1) & 0xFF == ord('q'):
		break
video_capture.release()
cv2.destroyALlWindows()
