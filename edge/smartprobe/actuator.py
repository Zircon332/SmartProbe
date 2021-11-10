import random
from pest_detection.pest_detection_model import Pest_Detector
from PIL import Image
import io
# P - pest
# W - water
# 0 - off
# 1 - on
model = Pest_Detector()

def generate_sprinkler_output(moisture, temperature):
    if moisture < 3000:
        return "W1"
    else:
        return "W0"

def generate_sprayer_output(image):
#     state = random.randrange(0, 3)
#     if state == 0:
#         return "P1"
#     else:
#         return "P0"
    frame = Image.open(io.BytesIO(image))
    if(model.detect(frame)):
        print("Pest Detected, Activating Pest Sprayer")
        return "P1"
    else:
        print("No Pest Detected for now")
        return "P0"

if __name__ == "__main__":
    model = Pest_Detector()