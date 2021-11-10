import os
import tensorflow as tf
# from object_detection.utils import config_util
from object_detection.utils import label_map_util
from object_detection.builders import model_builder
from PIL import Image
import numpy as np

DATASET = 'dataset'
MODELS = 'saved_model'
ANNOTATION = os.path.join(DATASET,'annotation')
# CHECKPOINTS = os.path.join(MODELS,'ssd_mobnet')
# MODEL_NAME = 'ssd_mobnet'
CONFIG_PATH = MODELS + '/pipeline.config'
SAVED_MODEL_NAME = 'frozen_inference_graph.pb'
PATH_TO_CKPT = os.path.join(MODELS,SAVED_MODEL_NAME)


class Pest_Detector:
    def __init__(self):
##        self._configs = config_util.get_configs_from_pipeline_file(CONFIG_PATH)
##         Build the model using model config
##        self._detection_model = model_builder.build(model_config=self._configs['model'],is_training=False)
##
##        restore checkpoint
##        self._checkpoint = tf.compat.v2.train.Checkpoint(model=self._detection_model)
##        latest checkpoint is ckpt-6
##        self._checkpoint.restore(os.path.join(CHECKPOINTS,'ckpt-4')).expect_partial()

        self._category_index = label_map_util.create_category_index_from_labelmap(ANNOTATION+'/label_map.pbtxt')

        self._detection_graph = tf.Graph()
        with self._detection_graph.as_default():
            od_graph_def = tf.compat.v1.GraphDef()
            with tf.io.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
                serialized_graph = fid.read()
                od_graph_def.ParseFromString(serialized_graph)
                tf.import_graph_def(od_graph_def, name='')
        

    def detect(self,frame):
##        print("detecting")
        with self._detection_graph.as_default():
            with tf.compat.v1.Session(graph=self._detection_graph) as sess:
                image_array = np.array(frame)
                image_np_expanded = np.expand_dims(image_array, axis=0)
                
                # Extract image tensor
                image_tensor = self._detection_graph.get_tensor_by_name('image_tensor:0')
                # Extract detection boxes
                boxes = self._detection_graph.get_tensor_by_name('detection_boxes:0')
                # Extract detection scores
                scores = self._detection_graph.get_tensor_by_name('detection_scores:0')
                # Extract detection classes
                classes = self._detection_graph.get_tensor_by_name('detection_classes:0')
                # Extract number of detectionsd
                num_detections = self._detection_graph.get_tensor_by_name('num_detections:0')

                (boxes, scores, classes, num_detections) = sess.run(
                [boxes, scores, classes, num_detections],
                feed_dict={image_tensor: image_np_expanded})

                classes = np.squeeze(classes).astype(np.int32)
                scores = np.squeeze(scores)

                max_boxes_to_draw = boxes.shape[0]
                min_score_thresh=.5

                detection = []

                for i in range(min(max_boxes_to_draw, boxes.shape[0])):
                    #If the bounding box has a score over 0.5
                    if scores is None or scores[i] > min_score_thresh:
                        # Draw the box
                        detected_class = classes[i]
                        category =  self._category_index[detected_class]
                        #Get the labeled class name
                        class_name = category['name']
                        detection.append(class_name)
##                        print(scores[i])
##                        print(class_name)

                return (len(detection)>0)

# 
# if __name__ == "__main__":
#     frame = Image.open('temp.bmp')
#     model = Pest_Detector()
#     print(model.detect(frame))
