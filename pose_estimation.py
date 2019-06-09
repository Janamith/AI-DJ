import json
import struct
import tensorflow as tf
import cv2
import numpy as np
import os
import yaml
import sys
import time 
from decode_multi_pose import decodeMultiplePoses
from decode_single_pose import decode_single_pose
from draw import drawKeypoints, drawSkeleton

color_table = [(0,255,0), (255,0,0), (0,0,255), (255, 255, 0), (0, 255, 255), (255, 0, 255)]

with open('config.yaml') as f:
    cfg = yaml.load(f)
    imageSize = cfg['imageSize']

cap = cv2.VideoCapture(0)
cap_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
cap_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
width_factor =  cap_width/imageSize
height_factor = cap_height/imageSize


# Load TFLite model and allocate tensors.
interpreter = tf.lite.Interpreter(model_path="../converted_model.tflite")
interpreter.allocate_tensors()

# Get input and output tensors.
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()
input_shape = input_details[0]['shape']
flag, frame = cap.read()
while flag:
    startime = time.time()
    orig_image = frame
    frame = cv2.resize(frame, (imageSize, imageSize))
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame = frame.astype(float)
    frame = frame * (2.0 / 255.0) - 1.0
    frame = np.array(frame, dtype=np.float32)
    frame = frame.reshape(1, imageSize, imageSize, 3)
    input_data = frame
    interpreter.set_tensor(input_details[0]['index'], input_data)
    interpreter.invoke()
    heatmaps_result = interpreter.get_tensor(output_details[0]['index']) 
    #print(heatmaps_result.shape)
    offsets_result = interpreter.get_tensor(output_details[1]['index'])
    displacementFwd_result = interpreter.get_tensor(output_details[2]['index'])
    displacementBwd_result = interpreter.get_tensor(output_details[3]['index'])
    poses = decodeMultiplePoses(heatmaps_result, offsets_result, \
                                            displacementFwd_result, \
                                            displacementBwd_result, \
                                            width_factor, height_factor)

    for idx in range(len(poses)):
        if poses[idx]['score'] > 0.2:
            color = color_table[idx]
            drawKeypoints(poses[idx], orig_image, color)
            drawSkeleton(poses[idx], orig_image)
    endtime = time.time()
    print('Time cost per frame : %f' % (endtime - startime))
    cv2.imshow("1", orig_image)
    cv2.waitKey(1)
    ret, frame = cap.read()
'''
# Test model on random input data.
print(input_shape)

#print(output_data)
'''