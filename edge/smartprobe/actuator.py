import random
from pest_detection.pest_detection_model import Pest_Detector

# P - pest
# W - water
# 0 - off
# 1 - on

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
    frame = Image.open(image)
    return modle.detect(frame)

if __name__ == "__main__":
    model = Pest_Detector()