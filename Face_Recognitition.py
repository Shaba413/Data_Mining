# -*- coding: utf-8 -*-
"""1920932_CSC417_Assignment6_Su22.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Kx8KMIixGgXCCAoppX2Tv7ABin3twVyx

#**Sumaia Anjum Shaba**
#**1920932**
#**Assignment 6**

#**Library Import**
"""

import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA as pca
from sklearn.datasets import fetch_lfw_people
from sklearn.model_selection import train_test_split
from time import time
import time
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
from sklearn import metrics

"""#**Get load Data**"""

def get_data():
    lfw_people = fetch_lfw_people(min_faces_per_person = 70,resize = 0.4)
    #The original dataset contains more than 13,000 images of faces collected from the web
    # print(lfw_people)
    # The extracted dataset will only retain pictures of people that have at least min_faces_per_person different pictures.
    n_samples, h, w = lfw_people.images.shape
    # print(n_samples) #1288  number of row is n_sample   (n_sample,n_fetaure)
    # print(h) #50
    # print(w) #37

    X = lfw_people.data
    # print(X.shape) #(1288, 1850) fetaure 1850
    y = lfw_people.target
    # print(y) #(1288,)    The target array is usually one dimensional, with length n_samples, and is generally contained in a NumPy array or Pandas Series
    #  we also generally work with a label or target array, which by convention we will usually call y
    return X,y,h,w

# resizefloat, default=0.5
# Ratio used to resize the each face picture.

# min_faces_per_person int, default=None
# The extracted dataset will only retain pictures of people that have at least min_faces_per_person different pictures.

"""#**PCA**
#Principal Component Analysis

"""

def PCA(X,k): #X=X_train
  avg=np.mean(X,axis=0) # row borabor
  centered=X-avg
  # print(centered.shape) #(1030, 1850)
  cov_matrix=np.cov(centered.T)  #createing covariance matrix using demean
  print(cov_matrix.shape) #(1850,1850)
  eigen_values,eigen_vects=np.linalg.eig(cov_matrix) # eigen value and eigen vector
  sorted_index= np.argsort(eigen_values)[::-1] # decending order e sort  .argsort will return the  indices of sorting array and as it will sort in a decending formate so (-1)

  eigen_values=eigen_values[sorted_index]

  eigen_vectors=eigen_vects[:,sorted_index]   # col gulo decending order rakhtache jate top eigen basis pai
  eigen_basis=eigen_vectors[:,0:k]  #(1850,12)    agei jehetu col gulo sort kore felchi so top 12 eigen gulo aitay thakbe
  # ((12,1850) dot (1850,1030)).T -> (12,1030).T ->(1030,12)
  reduced_X=(eigen_basis.T.dot(centered.T)).T  #(1030,12)
  return reduced_X,eigen_basis  # top 12 dimension eigen basis (1850,12)  and x_reduce hoiche (1850->12 col )

#Transform the data
# X_reduced = np.dot(eigenvector_subset.transpose(),X_meaned.transpose()).transpose()
# The final dimensions of X_reduced will be ( 20, 2 ) and originally the data was of higher dimensions ( 20, 5 ).


# Sort the Eigenvalues in the descending order along with their corresponding Eigenvector.irst column in our rearranged Eigen vector-matrix will be a principal component that captures the highest variability.

"""#**Calculated the distance for predict**"""

def get_distance(p1,p2):
    p = np.subtract(p1,p2)
    return np.linalg.norm(p)

"""#**Image show**"""

def show_image(data1,data2,h,w,index,p_index): #data1=xtest
    plt.figure()
    plt.subplot(1,2,1)
    data1 = np.array(data1,dtype=float)
    imdata = np.reshape(data1,(h,w))
    plt.title('Original Label: '+str(index))   #original test image
    plt.imshow(imdata)
    plt.subplot(1,2,2)
    data2 = np.array(data2,dtype=float)
    imdata = np.reshape(data2,(h,w))
    plt.title('Predicted Label: '+str(p_index))  #real image er sathe jeita perdict korche
    plt.imshow(imdata)

"""#**Eigen Face show train**"""

def show_eigen_faces(data,h,w):
  plt.figure()
  # print(data.shape[1]) #12   col shape findout korar jonno data.shape[1]  np.shape(data) will give the array shape
  for i in range(data.shape[1]):
    temp=np.array(data[:,i],dtype=float)
    idata=np.reshape(temp,(h,w))
    plt.title('Eigen Face: '+str(i+1))  #i+1 coz i zero theke shuru but eigen face 1 theke start korar jonno
    plt.imshow(idata)
    plt.show()

"""#**Main Function**

"""

def main():
    k = 12
    t = time.time()
    X,y,h,w = get_data()
    # print(X.shape) #(1288, 1850)  1030+258=1288 X_train+X_test split korche 0.2
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2, random_state = 42)
    # test_size should be between 0.0 and 1.0 and represent the proportion of the dataset to include in the test split.
    # random_state Controls the shuffling applied to the data before applying the split
    # print(X_train.shape) #(1030,1850)
    # print(X_test.shape)  #(258, 1850)
    # print(y_train.shape) #(1030,)
    # print(y_test) #(258,)


    X_reduced,eigen_basis = PCA(X_train,k)
    # print(X_reduced.shape)  #(1030, 12)  X_tarin dimission reduced 1850 theke 12  and row 1030
    # print(eigen_basis.shape) #(1288,12)

    X_test_meaned = X_test - np.mean(X_train,axis=0)   #test image ke centered e  fai=test=avg demean vector
    # print(X_test_meaned.shape) #(258,1850)

    X_test_reduced = eigen_basis.T.dot(X_test_meaned.T).T
    #((1288,12).T->(12,1288) dot (258,1850).T->(1850,258) )->(12,258).T->(258,12)
    # print(X_test_reduced.shape)  #(258,12)


    show_eigen_faces(eigen_basis,h,w)
    count = 0

    r = X_train.shape[0]   # row er length shape[0]=row ,shape[1]=col
    # print(r) #1030 distance calculated er jonno
    # print(len(y_test)) #258

    for i in range(len(y_test)):
        dist = np.zeros(r)  # as there are 1030 train image ache so sob gular sathe distance calculated kroar jonno row size

        for j in range(r):
            dist[j] = get_distance(X_test_reduced[i],X_reduced[j])   # train_reduce and test_reduce distance calculated

        min_index = np.argmin(dist)   #Returns the indices of the minimum values along an axis.
        if(y_train[min_index] == y_test[i]):  #label match korteche match hole count increment korbe
            count+=1

        show_image(X_test[i],X_train[min_index],h,w,y_test[i],y_train[min_index])



    print("Total: ",len(y_test))
    print("Accurate: ",count)
    print("accuracy:",count/len(y_test)*100)

    d=X_reduced-X_test_reduced[:, np.newaxis, 0:]
    distance = np.linalg.norm(d,axis=2)
    min_distance_index = np.argmin(distance, axis=1)
    confusion_matrix = metrics.confusion_matrix(y_test, y_train[min_distance_index])
    cm_display = metrics.ConfusionMatrixDisplay(confusion_matrix = confusion_matrix, display_labels = [False, True])
    cm_display.plot()
    plt.show()

    print("Total Time : ",time.time()-t)

if __name__=="__main__":
    main()

def PCA2(X,k):
  avg=np.mean(X,axis=0)
  centered=X-avg
  # cov_matrix=np.cov(centered.T)
  # eigen_values,eigen_vects=np.linalg.eig(cov_matrix)
  # sorted_index= np.argsort(eigen_values)[::-1]
  # eigen_values=eigen_values[sorted_index]
  # eigen_vectors=eigen_vects[:,sorted_index]
  # eigen_basis=eigen_vects[:,0:k]
  # reduced_X=eigen_basis.T.dot(centered.T).T
  return centered

def main():
    k = 12
    t=time.time()
    X,y,h,w = get_data()
    # print(X.shape)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2, random_state = 42)
    centered = PCA2(X_train,k)
    X_test_meaned = X_test - np.mean(X_train,axis=0)   #test image ke centered e  fai=test=avg
    # X_test_reduced = eigen_basis.T.dot(X_test_meaned.T).T

    # show_eigen_faces(eigen_basis,h,w)
    count = 0

    r = X_train.shape[0]
    # print(r) #1030 distance calculated er jonno
    # print(len(y_test)) #258

    for i in range(len(y_test)):
        dist = np.zeros(r)

        for j in range(r):
            dist[j] = get_distance(X_test_meaned[i],centered[j])

        min_index = np.argmin(dist)
        if(y_train[min_index] == y_test[i]):
            count+=1

        show_image(X_test[i],X_train[min_index],h,w,y_test[i],y_train[min_index])



    print("Total: ",len(y_test))
    print("Accurate: ",count)

    print("accuracy:",count/len(y_test))
    d=X_train-X_test[:, np.newaxis, 0:]
    distance = np.linalg.norm(d,axis=2)
    min_distance_index = np.argmin(distance, axis=1)
    confusion_matrix = metrics.confusion_matrix(y_test, y_train[min_distance_index])
    cm_display = metrics.ConfusionMatrixDisplay(confusion_matrix = confusion_matrix, display_labels = [False, True])
    cm_display.plot()
    plt.show()
    print(time.time()-t)

if __name__=="__main__":
    main()