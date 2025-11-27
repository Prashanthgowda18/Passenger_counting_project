import numpy as np
from scipy.spatial import distance as dist
from collections import OrderedDict
import time

class TrackedObject:
    def __init__(self, objectID, centroid, bbox):
        self.objectID = objectID
        self.centroid = centroid
        self.bbox = bbox
        self.disappeared = 0
        self.history = [centroid]
        self.last_seen = time.time()
        self.entered = False
        self.exited = False
        self.moved_right = False
        self.initial_position = centroid
        self.passenger_number = 0  # Sequential passenger number

class CentroidTracker:
    def __init__(self, maxDisappeared=60, maxDistance=80):
        self.nextObjectID = 0
        self.objects = OrderedDict()
        self.maxDisappeared = maxDisappeared
        self.maxDistance = maxDistance

    def register(self, centroid, bbox):
        to = TrackedObject(self.nextObjectID, centroid, bbox)
        self.objects[self.nextObjectID] = to
        self.nextObjectID += 1

    def deregister(self, objectID):
        if objectID in self.objects:
            del self.objects[objectID]
    
    def check_right_movement(self, objectID, frame_width):
        """Check if object has moved to the right side of the frame"""
        if objectID not in self.objects:
            return False
        
        obj = self.objects[objectID]
        if len(obj.history) < 2:
            return False
        
        # Get current and initial positions
        current_x = obj.centroid[0]
        initial_x = obj.initial_position[0]
        
        # Check if moved significantly to the right
        right_threshold = frame_width * 0.6  # 60% from left edge
        moved_right = current_x > right_threshold
        significant_movement = abs(current_x - initial_x) > 20  # minimum 20 pixels movement
        
        return moved_right and significant_movement

    def update(self, rects):
        """
        rects: list of bounding boxes (x1, y1, x2, y2)
        Returns: dict of objectID → TrackedObject
        """
        if len(rects) == 0:
            for objectID in list(self.objects.keys()):
                self.objects[objectID].disappeared += 1
                if self.objects[objectID].disappeared > self.maxDisappeared:
                    self.deregister(objectID)
            return self.objects

        inputCentroids = []
        for (x1, y1, x2, y2) in rects:
            cX = int((x1 + x2) / 2.0)
            cY = int((y1 + y2) / 2.0)
            inputCentroids.append((cX, cY))

        if len(self.objects) == 0:
            for i, centroid in enumerate(inputCentroids):
                self.register(centroid, rects[i])
        else:
            objectIDs = list(self.objects.keys())
            objectCentroids = [self.objects[oid].centroid for oid in objectIDs]

            D = dist.cdist(np.array(objectCentroids), np.array(inputCentroids))
            rows = D.min(axis=1).argsort()
            cols = D.argmin(axis=1)[rows]

            usedRows, usedCols = set(), set()

            for (row, col) in zip(rows, cols):
                if row in usedRows or col in usedCols:
                    continue
                if D[row, col] > self.maxDistance:
                    continue

                objectID = objectIDs[row]
                self.objects[objectID].centroid = inputCentroids[col]
                self.objects[objectID].bbox = rects[col]
                self.objects[objectID].history.append(inputCentroids[col])
                self.objects[objectID].disappeared = 0
                self.objects[objectID].last_seen = time.time()

                usedRows.add(row)
                usedCols.add(col)

            unusedRows = set(range(0, D.shape[0])).difference(usedRows)
            for row in unusedRows:
                objectID = objectIDs[row]
                self.objects[objectID].disappeared += 1
                if self.objects[objectID].disappeared > self.maxDisappeared:
                    self.deregister(objectID)

            unusedCols = set(range(0, D.shape[1])).difference(usedCols)
            for col in unusedCols:
                self.register(inputCentroids[col], rects[col])

        return self.objects