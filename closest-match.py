#! /usr/bin/python2
import sys, cv2, time, os
import openface, numpy
from math import log1p, log

IMG_DIM = 96

modelDir = os.path.join('openface', 'models')
dlibModelDir = os.path.join(modelDir, 'dlib')
dlibFacePredictor = os.path.join(dlibModelDir, "shape_predictor_68_face_landmarks.dat")
openfaceModelDir = os.path.join(modelDir, 'openface')
networkModel = os.path.join(openfaceModelDir, 'nn4.small2.v1.t7')

align = openface.AlignDlib(dlibFacePredictor)
net = openface.TorchNeuralNet(networkModel, IMG_DIM)

def getRep(imgPath):
    bgrImg = cv2.imread(imgPath)
    if bgrImg is None:
        raise Exception("Unable to load image: {}".format(imgPath))
    rgbImg = cv2.cvtColor(bgrImg, cv2.COLOR_BGR2RGB)

    start = time.time()
    bb = align.getLargestFaceBoundingBox(rgbImg)
    if bb is None:
        raise Exception("Unable to find a face: {}".format(imgPath))

    start = time.time()
    alignedFace = align.align(IMG_DIM, rgbImg, bb,
                              landmarkIndices=openface.AlignDlib.OUTER_EYES_AND_NOSE)

    start = time.time()
    return net.forward(alignedFace)

class MultiBinaryTree:
    class Node:
        def __init__(self, key, value):
            self.key = key
            self.values = [value]

        def find(self, key):
            if key == self.key: return self.values
            elif key < self.key and hasattr(self, 'lesser'):
                return self.lesser.find(key)
            elif key > self.key and hasattr(self, 'greater'):
                return self.greater.find(key)
            else: return None

        def near(self, key):
            for x in self.values: yield x
            if key < self.key and hasattr(self, 'lesser'):
                for x in self.lesser.near(key): yield x
            elif key > self.key and hasattr(self, 'greater'):
                for x in self.greater.near(key): yield x

        def insert(self, key, value):
            key = key
            if key == self.key: self.values.append(value)
            elif key < self.key:
                if hasattr(self, 'lesser'): self.lesser.insert(key, value)
                else: self.lesser = MultiBinaryTree.Node(key, value)
            elif key > self.key:
                if hasattr(self, 'greater'): self.greater.insert(key, value)
                else: self.greater = MultiBinaryTree.Node(key, value)

        def __iter__(self):
            for x in getattr(self, 'lesser', []): yield x
            for x in self.values: yield x
            for x in getattr(self, 'greater', []): yield x

    def find(self, key):
        if not hasattr(self, 'indices'): return None

        def l2_dist(other):
            d = key - other[0]
            return numpy.dot(d, d)
        return min(self.indices[0].find(key[0]), key=l2_dist)[1]

    def nearest(self, key):
        def l2_dist(other):
            d = key - other[0]
            return numpy.dot(d, d)
        return min((v for index in getattr(self, 'indices', []) for k in key
                    for v in index.near(k)), key=l2_dist)

    def insert(self, key, value):
        if hasattr(self, 'indices'):
            for index, key_item in zip(self.indices, key):
                index.insert(key_item, (key, value))
        else:
            self.indices = [MultiBinaryTree.Node(k, (key, value)) for k in key]

index = MultiBinaryTree()
for fname in sys.argv[2:]:
    print ",",
    try:
        index.insert(getRep(fname), fname)
    except Exception, ex:
        print ex
print

inface = getRep(sys.argv[1])
face, filename = index.nearest(inface)
d = inface - face
d = numpy.dot(d, d)
if d <= 1:
    score = 80 + (1 - d) * 20
elif d <= 1.5:
    _ = (1.5 - d)/0.5
    score = 20 + _ * 60
elif d <= 3:
    _ = (3 - d)/1.5
    score = _ * 20
else:
    score = 0
print filename, (3 - d)/3 * 100, "%", score, "%", d

# Clara's furthest match #55979, dist 2.88
# closest: 1.256 #59374
