import tensorflow as tf  

converter = tf.lite.TFLiteConverter.from_session('./checkpoints')
tflite_model = converter.convert()
open('converted_model.tflite', 'wb').write(tflite_model)