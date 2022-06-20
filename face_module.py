from sklearn.neighbors import NearestNeighbors
import face_recognition
import urllib.request
import numpy as np
import tempfile
import cv2


#----------------------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------------


class Face:  
  def __init__(self):
  #...............
    self._neighbors_=5
    self._model_ = NearestNeighbors(n_neighbors=self._neighbors_, algorithm='brute', metric='euclidean')
  
  #-------------------------------------------------
  
  def encode(self,path):
    #...............
    try:
      if 'http' in path:
        format = '.'+path.split('.')[-1]
        temp = tempfile.NamedTemporaryFile(suffix=format)
        urllib.request.urlretrieve(path,temp.name)
        img = face_recognition.load_image_file(temp.name)
        temp.close()
      else: img = face_recognition.load_image_file(path)
      return face_recognition.face_encodings(img)[0]
    except: return np.zeros(128)
      
  #-------------------------------------------------
  
  def search( self, Query_Path, data_arr, vector_arr ):
    #...............
    frame = cv2.imread(Query_Path)
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_small_frame)
    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
    self._model_.fit(vector_arr)
    result = []
    for face_encoding in face_encodings:
      distances,indices = self._model_.kneighbors([face_encoding])
      distances,indices = distances[0],indices[0]
      
      sub_data_arr = [data_arr[i]  for i in indices]
      sub_vector_arr = [vector_arr[i]  for i in indices]
      
      matches = face_recognition.compare_faces(sub_vector_arr, face_encoding)
      face_distances = face_recognition.face_distance(sub_vector_arr, face_encoding)
      
      best_match_index = np.argmin(face_distances)
      if matches[best_match_index] and face_distances[best_match_index]<0.55:
          data = sub_data_arr[best_match_index]
          result.append(data)
    return result
