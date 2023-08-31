# -*- coding: utf-8 -*-
"""1920932_CSE417_Assignment7.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1U2aPHd2geeJKHHrKLNmRDXsHBi-xOGoJ

#**Mounting**
"""

from google.colab import drive
drive.mount('/content/drive')

"""#**Import Libaray**"""

import numpy as np
from keras.datasets import mnist
import random
import sys
import time
from sklearn.metrics import confusion_matrix
from scipy.special import comb
from sklearn.metrics import davies_bouldin_score
from sklearn.metrics import rand_score
from matplotlib import pyplot as plt
from numpy import linalg as LA
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
from sklearn.metrics import classification_report
from sklearn.cluster import KMeans as KMeans_
from sklearn.decomposition import PCA as pca_
import warnings
warnings.filterwarnings('ignore')
np.set_printoptions(threshold=sys.maxsize)
import pandas as pd
import nltk
nltk.download('punkt')
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
nltk.download('stopwords')
from nltk.stem import PorterStemmer
from collections import Counter
from scipy import sparse
np.set_printoptions(suppress=True)
np.seterr(invalid='ignore')
from sklearn.metrics.cluster import contingency_matrix
import gc
from sklearn.model_selection import train_test_split
from sklearn.manifold import TSNE
from warnings import simplefilter

"""#**Kmeans**"""

def initialize_centroids_simple(data, dimension, k):
    centroids = np.zeros((k,dimension))
    r,c=data.shape
    rand_index=random.sample(range(0,r),k)
    centroids=data[rand_index]
    return centroids

def kmeans(data, r, c, k):
    # centroids = [[centroid0], [centroid1], [centroid2], [centroid3], ....]
    centroids = initialize_centroids_simple(data, c, k)
    # cluster_affiliation = [index0 centroid number, index1 centroid number, index2 centroid number] (index till number of rows in data)
    cluster_affiliation = np.empty((data.shape[0]))
    cluster_affiliation[:] = None
    flag = 1
    Jprev = 0
    min_distance=np.array([])
    min_distance_index=np.array([])
    while flag:
        J = 0
        # clutser_point_count= [cluster0 #points, cluster1 #points, ..., clusterK-1 #points]
        clutser_point_count = np.zeros(k)
        # distance = for every row in data for every centroid Euclidean distance counted
        # distance = [[point0 dist from centroid0, dist from centroid1, ....],[point1 dist from centroid0, dist from centroid1, ....],[],[]]
        distance = np.linalg.norm(centroids[np.invert(np.isnan(centroids).all(axis=1))]-data[:, np.newaxis, 0:], axis=2)
        min_distance = np.min(distance, axis=1)
        min_distance_index = np.argmin(distance, axis=1)
        check_ca = cluster_affiliation != min_distance_index
        cluster_affiliation[check_ca] = min_distance_index[check_ca]
        u, count = np.unique(cluster_affiliation, return_counts=True)
        clutser_point_count[u.astype(int)] = count
        centroids = np.zeros((k, c))
        for i in range(k):
            if clutser_point_count[i] != 0:
                indices = np.where(cluster_affiliation == i)[0]
                centroids[i] = np.sum(
                    data[indices], axis=0) / clutser_point_count[i]
        J = np.sum(min_distance**2)
        J = J/r

        # Terminate the while loop based on termination criteria. Write your code to turn flag = false
        if abs(J-Jprev) < 10**-5:
            flag = False
            print(clutser_point_count)
        Jprev = J
    return (centroids, cluster_affiliation, J, min_distance, min_distance_index, clutser_point_count)

# import numpy as np
# data=np.array([[10,2,3],[6,6,3],[-6,6,3],[1,2,4]])
# centroids=np.array([[10,2,3],[6,6,3]])
# print(data[:, np.newaxis])
# centroids-data[:, np.newaxis]

"""#** db index**"""

def db_index(centroids, clutser_point_count, cluster_affiliation, min_distance, K):
    db=np.array([])
    for i in range(K):
      ratio=np.array([])
      if clutser_point_count[i] != 0:
        cluster_points_mean_dist_i= np.mean(min_distance[np.where(cluster_affiliation == i)[0]])
      for j in range(K):
        if j==i:
          continue
        else:
          if clutser_point_count[j] != 0:
              cluster_points_mean_dist_j=np.mean(min_distance[np.where(cluster_affiliation == j)[0]])
              cluster_centroid_dist= np.linalg.norm(centroids[i]-centroids[j])
              ratio=np.hstack((ratio,(cluster_points_mean_dist_i+cluster_points_mean_dist_j)/cluster_centroid_dist))
      db=np.hstack((db,np.max(ratio)))
    db=np.sum(db)/K
    return db

"""### dunn index"""

def dunn_index(centroids, clutser_point_count, cluster_affiliation, min_distance, K):
    max_avg_cluster_point_dist=np.array([])
    min_cluster_centroid_dist=np.array([])
    # cluster_centroid_dist=np.array([])
    for i in range(K):
      if clutser_point_count[i] != 0:
        max_avg_cluster_point_dist= np.hstack((max_avg_cluster_point_dist,np.mean(min_distance[np.where(cluster_affiliation == i)[0]])))
      for j in range(K):
        if j<=i:
          continue
        else:
          min_cluster_centroid_dist= np.hstack((min_cluster_centroid_dist, np.linalg.norm(centroids[i]-centroids[j])))
    dunn=np.min(min_cluster_centroid_dist)/np.max(max_avg_cluster_point_dist)
    return dunn

"""#**PCA**"""

def PCA(X,k):
  A = X - np.mean(X,axis=0)
  cov = np.cov(A.T)
  w,v = LA.eigh(cov)
  sorted_index = np.argsort(w)[::-1]
  eigen_vals = w[sorted_index[0:k]]
  eigen_basis = v[:,sorted_index[0:k]]
  reduced_X = np.dot(eigen_basis.T,A.T).T
  return reduced_X,eigen_basis

"""# MNIST

## 1. MNIST (PCA)
"""

def load():
    (X, Y), (test_X, test_y) = mnist.load_data()
    h,r,c=X.shape
    X=X.reshape(h,-1)/255.0
    return X,Y,r,c

"""#**reconstruct**"""

def reconstruct(centroids,eigen_basis,mean):
    centroids = np.dot(centroids,eigen_basis.T)+mean
    return centroids

"""#**show_centroids**"""

# def show_centroids(num_row,num_col,cluster_labels,images):
#     fig, axes = plt.subplots(num_row, num_col, figsize=(4*num_col,4*num_row))
#     for i, ax in enumerate(axes.flat):
#         for key, value in cluster_labels.items():
#             if i in value:
#                 ax.set_title('Inferred Label: {}'.format(key), color='blue')
#         ax.imshow(images[i],cmap=plt.cm.gray)
#         ax.axis('off')
#     # plt.tight_layout()
#     plt.show()

def plot_centroids(num_row,num_col,images):
  fig, axes = plt.subplots(num_row, num_col, figsize=(1.5*num_col,2*num_row))
  for i in range(images.shape[0]): #row
      ax = axes[i//num_col, i%num_col]
      ax.imshow(images[i], cmap='gray')
      # plt.imshow(images[i], cmap='gray')

  plt.tight_layout()
  plt.show()

"""#**plot Data*"""

def plot_data(X_reduced,ca,centroids,no_data):
  rand_index=random.sample(range(0,X_reduced.shape[0]),no_data)
  fig = plt.figure(figsize=(10,10))
  ax = plt.axes(projection='3d')
  ax.scatter(X_reduced[rand_index,0], X_reduced[rand_index,1], X_reduced[rand_index,2], s=30, c=ca[rand_index],cmap=plt.cm.Paired,alpha=1)
  l=[]
  u=np.unique(ca)

  ax.scatter(centroids[:,0],centroids[:,1],centroids[:,2],s=140,c=u,cmap=plt.cm.Paired,alpha=1)
  plt.show()

"""## 2. MNIST (PCA)

#**main**
"""

# def main():
#     K = 10
#     n_component=12
#     #load data
#     X,Y,r_,c_ = load()
#     #reduce dimension (PCA)
#     X_reduced,eigen_basis = PCA(X,n_component)
#     r, c = X_reduced.shape
#     #run kmeans
#     centroids, cluster_affiliation, J, min_distance, min_distance_index, clutser_point_count= kmeans(X_reduced, r, c, K)
#     #get actual predic labels
#     cluster_labels =clusterLabels(cluster_affiliation, Y, K)
#     print("a")
#     print(cluster_labels) #{6: [0], 1: [1, 5], 8: [2], 7: [3], 2: [4], 9: [6], 0: [7], 3: [8], 4: [9]}
#     predicted_labels = data_labels(cluster_affiliation, cluster_labels)
#     #show centroid images
#     re_centroids=reconstruct(centroids,eigen_basis,np.mean(X,axis=0))
#     images=re_centroids.reshape(-1,r_,c_)
#     num_row = 2
#     num_col = 5
#     show_centroids(num_row,num_col,cluster_labels,images)
#     #mse
#     print('J: ',J)
#     db= davies_bouldin_score(X_reduced, cluster_affiliation)
#     print('Davies–Bouldin index : ',db)
#     #dunn index
#     dunn= dunn_index(centroids, clutser_point_count, cluster_affiliation, min_distance, K)
#     print('Dunn index: ', dunn)
#     #purity
#     conf=confusion_matrix(Y, predicted_labels)
#     purity=np.sum(np.amax(conf, axis=0)) / r
#     print('Purity: ', purity)
#     print("Rand Index : ",rand_score(Y,predicted_labels))
#     plot_data(X_reduced,cluster_affiliation,centroids,100)

# if __name__ == "__main__":
#     main()

# def show_image(data):

#     plt.imshow(data,cmap='gray')
#     plt.show()

"""#**Main**"""

def main():
    K = 10
    n_component=12
    #load data
    X,Y,r_,c_ = load()
    #reduce dimension (PCA)
    X_reduced,eigen_basis = PCA(X,n_component)
    r, c = X_reduced.shape
    #run kmeans
    centroids, cluster_affiliation, J, min_distance, min_distance_index, clutser_point_count= kmeans(X_reduced, r, c, K)
    re_centroids=reconstruct(centroids,eigen_basis,np.mean(X,axis=0))
    images=re_centroids.reshape(-1,r_,c_)
    num_row = 2
    num_col = 5
    plot_centroids(num_row,num_col,images)

    #mse
    print('J: ',J)
    db= davies_bouldin_score(X_reduced, cluster_affiliation)
    print('Davies–Bouldin index : ',db)
    #dunn index
    dunn= dunn_index(centroids, clutser_point_count, cluster_affiliation, min_distance, K)
    print('Dunn index: ', dunn)
    #purity
    conf=confusion_matrix(Y, cluster_affiliation)
    purity=np.sum(np.amax(conf, axis=0)) / r
    print('Purity: ', purity)
    print("Rand Index : ",rand_score(Y,cluster_affiliation))
    plot_data(X_reduced,cluster_affiliation,centroids,100)

if __name__ == "__main__":
    main()

"""#** 1. MNIST (Full dim)**"""

def main():
    K = 10
    #load data
    X,Y,r_,c_ = load()
    r, c = X.shape
    #run kmeans
    centroids, cluster_affiliation, J, min_distance, min_distance_index, clutser_point_count= kmeans(X, r, c, K)
    # #get actual predic labels
    # cluster_labels =clusterLabels(cluster_affiliation, Y, K)
    # print(cluster_labels)
    # # predicted_labels = data_labels(cluster_affiliation, cluster_labels)
    # # #show centroid images
    images=centroids.reshape(-1,r_,c_)
    num_row = 2
    num_col = 5
    plot_centroids(num_row,num_col,images)
    #mse
    print('J: ',J)
    #db index

    db = davies_bouldin_score(X, cluster_affiliation)
    print('Davies–Bouldin index : ',db)
    #dunn index
    dunn= dunn_index(centroids, clutser_point_count, cluster_affiliation, min_distance, K)
    print('Dunn index: ', dunn)
    #purity
    conf=confusion_matrix(Y, cluster_affiliation)
    purity=np.sum(np.amax(conf, axis=0)) / r
    print('Purity: ', purity)
    #rand index

    print("Rand Index : ",rand_score(Y,cluster_affiliation))




if __name__ == "__main__":
    main()

"""## 3. MNIST SVM Classifier"""

from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from keras.datasets import mnist
from sklearn.metrics import f1_score
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix
import numpy as np

def loadall():
    (X_train, Y_train), (X_test, Y_test) = mnist.load_data()
    h_train,r_train,c_train=X_train.shape
    X_train=X_train.reshape(h_train,-1)/255.0
    h_test,r_test,c_test=X_test.shape
    X_test=X_test.reshape(h_test,-1)/255.0
    return X_train,Y_train,X_test,Y_test

def preprocessTestData(X_test,eigen_basis):
  A_X_test = X_test - np.mean(X_test,axis=0)
  reduced_X_test = np.dot(eigen_basis.T,A_X_test.T).T
  return reduced_X_test

def svc_clf(X,y,X_test,y_test):
    svc = SVC(kernel='linear')
    svc.fit(X,y)
    y_pred = svc.predict(X_test)

    f1score = f1_score(y_test,y_pred,average='macro')
    accuracy = accuracy_score(y_test,y_pred)
    print(classification_report(y_test, y_pred))
    print("F1 score: ",f1score)
    print('Accuracy: ',accuracy)
    print("Confusion matrix: \n",confusion_matrix(y_test, y_pred))

def main():
    X_train,y_train, X_test, y_test = loadall()
    #Full Dimension
    print("For Full Dimension: ")
    svc_clf(X_train,y_train,X_test,y_test)

    #Reduced Dimension
    num_component = 12
    X_train_reduced,eigen_basis = PCA(X_train,num_component)
    X_test_reduced = preprocessTestData(X_test,eigen_basis)
    print("For Reduced Dimension: ")
    svc_clf(X_train_reduced,y_train,X_test_reduced,y_test)


if __name__=='__main__':
    main()

"""#**Assignment 4**

"""

def main():
    K = 10
    X,Y,r_,c_ = load()
    # X=X[0:1000]
    r, c = X.shape
    start = time.time()
    centroids, cluster_affiliation, J, min_distance, min_distance_index, clutser_point_count= kmeans(X, r, c, K)
    images=centroids.reshape(-1,r_,c_)
    num_row = 2
    num_col = 5
    # plot images
    plot_centroids(num_row,num_col,images)
    print('J: ',J)
      #show centroids image by reshaping


    db = davies_bouldin_score(X, cluster_affiliation)
    print('Davies–Bouldin index: ',db)

    dunn= dunn_index(centroids, clutser_point_count, cluster_affiliation, min_distance, K)
    print('Dunn index: ', dunn)

    conf=confusion_matrix(Y, cluster_affiliation)
    purity=np.sum(np.amax(conf, axis=0)) / r
    print('Purity: ', purity)


    print("Rand Index : ",rand_score(Y,cluster_affiliation))
    print('Duration: %s' % (time.time() - start))

    #plot 3d
    rand_index=random.sample(range(0,r),1000)
    fig = plt.figure(figsize=(10,10))
    ax = plt.axes(projection='3d')
    simplefilter(action='ignore', category=FutureWarning)
    m=TSNE(n_components=3)
    tsne_f=m.fit_transform(X[rand_index])
    x=tsne_f[:,0]
    y=tsne_f[:,1]
    z=tsne_f[:,2]
    ax.scatter(x,y,z,c=cluster_affiliation[rand_index],cmap=plt.cm.tab20)
    plt.show()
    # tsne_c=m.fit_transform(centroids)
    # xc=tsne_c[:,0]
    # yc=tsne_c[:,1]
    # zc=tsne_c[:,2]
    # ax.scatter(xc,yc,zc, marker="x",s=50,linewidths=3,color="r")
    # plt.show()

if __name__ == "__main__":
    main()

"""#**Assignment 4**

#**TEXT**

#**Load Data**
"""

def load_data(filepath):
  # temp_df=pd.read_csv(filepath,encoding = "unicode_escape",engine='python')
  temp_df=pd.read_csv(filepath)
  temp_df = temp_df[temp_df['text'].notna()]
  df=pd.DataFrame({'text': temp_df['text'].astype(str), 'topic':temp_df['topic'].astype(str)})

  return df

"""#**Tokennize**"""

def tokenize(df):
  #tokenizing
  regexp = RegexpTokenizer('\w+')
  df['text_token']=df['text'].apply(regexp.tokenize)
  #normalize
  df['text_token'] = df['text_token'].apply(lambda x: [item.lower() for item in x])
  #stemming
  df['text_token'] = df['text_token'].apply(lambda x: [PorterStemmer().stem(item) for item in x ])
  df['text_token'] = df['text_token'].apply(lambda x: [item for item in x if item.isalpha() and len(item)>1])
  #discard stopwords
  stopwords = nltk.corpus.stopwords.words("english")
  df['text_token'] = df['text_token'].apply(lambda x: [item for item in x if item not in stopwords])
  return df

"""#**Data Pre-Processing**"""

def preprocessing(df):
  # df = df[df['topic'].isin(['pcmasterrace','nfl','news','relationships','movies'])]
  df=tokenize(df)
  df = df[df.astype(str)['text_token']!='[]']
  docs=df['text_token'].tolist()
  topics=df['topic'].tolist()
  print(len(docs))
  return docs, topics

"""#**Get Unique Word**"""

def get_unique_words(docs):
  c = Counter()
  for doc in docs:
      c.update(doc)
  return c

# import numpy as np
# x=['abcd','abcd','efgh','abc','abs','s','s']
# c = Counter()
# for doc in x:
#   c.update(doc)
# print(c)
# words,count=zip(*c.most_common())
# print(words)
# print(count)
# counts=np.array(count)
# print(counts)
# zips_words_ind=np.where(np.logical_and(np.array(counts)>1, np.array(counts)<=4))[0]
# print(zips_words_ind)
# unique_words=np.array(words)[zips_words_ind]
# print(unique_words)

"""#**Main**"""

def main():
  start = time.time()
  filepath='/content/drive/MyDrive/Data Mining/reddit_data.csv'
  df=load_data(filepath)
  #process data
  docs,topics=preprocessing(df)
  # unique_words,frequency=get_unique_words(docs)
  freq=get_unique_words(docs)   # Counter({'a': 2, 'b': 2, 'c': 2, 'd': 2, 'e': 1, 'f': 1, 'g': 1, 'h': 1})
  words, counts = zip(*freq.most_common())
  # words: ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h')
  # counts:(2, 2, 2, 2, 1, 1, 1, 1)

  counts=np.array(counts) #[2 2 2 2 1 1 1 1]
  zips_words_ind=np.where(np.logical_and(np.array(counts)>50, np.array(counts)<500))[0]  # ai logic er modday porle sei gulo r index return
  unique_words=np.array(words)[zips_words_ind] #  word gulo store
  print(len(unique_words))

  #tfs
  tfs = np.zeros((len(docs),len(unique_words)),dtype=np.int16)
  for i,doc in enumerate(docs):
    tf = dict.fromkeys(unique_words, 0)
    for word in doc:
      if word in tf.keys():  #tf: apple:0,banana:0 tf.key will : apple,banan
        tf[word] += 1
    tfs[i]=list(tf.values())
  tfs=sparse.csr_matrix(tfs)

  a=0.4
  count_vectors_inf=np.where(tfs.toarray()==0,float('inf'),tfs.toarray())
  n_tfs=np.where(count_vectors_inf==float('inf'),a,a+(1-a)*tfs.toarray()/np.max(tfs.toarray(),axis=1).reshape(-1,1))
  #df
  df=np.sum(np.where(tfs.toarray()>=1,1,0),axis=0)
  idf=1+np.log(len(docs)/df).reshape(1,-1)
  #tf-idf
  ntf_idf=(n_tfs*idf).astype(np.float32)
  del tfs,n_tfs,count_vectors_inf,df,idf
  gc.collect()
  #kmeans
  k=5
  r,c=ntf_idf.shape
  centroids, cluster_affiliation, J, min_distance, min_distance_index, clutser_point_count=kmeans(ntf_idf, r, c, k)
  print('J: ',J)

  db= db_index(centroids, clutser_point_count, cluster_affiliation, min_distance, k)
  print('Davies–Bouldin index: ',db)

  dunn= dunn_index(centroids, clutser_point_count, cluster_affiliation, min_distance, k)
  print('Dunn index: ', dunn)

  conf=contingency_matrix(topics, cluster_affiliation)
  purity=np.sum(np.amax(conf, axis=0)) / r
  print('Purity: ', purity)


  print("Rand Index : ",rand_score(topics,cluster_affiliation))

  #plot 3d
  rand_index=random.sample(range(0,r),1000)
  fig = plt.figure(figsize=(10,10))
  ax = plt.axes(projection='3d')
  simplefilter(action='ignore', category=FutureWarning)
  m=TSNE(n_components=3)
  tsne_f=m.fit_transform(ntf_idf[rand_index])
  x=tsne_f[:,0]
  y=tsne_f[:,1]
  z=tsne_f[:,2]
  ax.scatter(x,y,z,c=cluster_affiliation[rand_index],cmap=plt.cm.tab20)
  plt.show()

  print('Duration: %s' % (time.time() - start))
if __name__ == "__main__":
  main()

"""#**Draft**"""

# t=['48' ,'movies', 'nan' ,'news' ,'nfl' ,'pcmasterrace', 'relationships','relationships','relationships']
# topics=['movies' ,'news' ,'nfl' ,'pcmasterrace', 'relationships']
# t=np.where(t == topics[0], 0,
#   (np.where(t == topics[1], 1,
#     (np.where(t == topics[2], 2,
#       (np.where(t == topics[3], 3,4)))))))
#         # (np.where(t == topics[4], 4, 5))))))))#)
# print(t)
# # print(np.where(t==topics[4],4,1))

"""#Assignment 7**

#**Que 2 TEXT**

#**Get Word Frequency**
"""

def get_word_freq(docs):
  c = Counter()
  for doc in docs:
      c.update(doc)
  return c

"""#**get_unique_words**"""

def get_unique_words2(freq,range_from,range_to):
  words, counts = zip(*freq.most_common())
  counts=np.array(counts)
  zips_words_ind=np.where(np.logical_and(np.array(counts)>range_from, np.array(counts)<range_to))[0]
  unique_words=np.array(words)[zips_words_ind]
  return unique_words

"""#**Get TF**"""

def get_tf(docs,unique_words):
  tfs = np.zeros((len(docs),len(unique_words)),dtype=np.int16)
  for i,doc in enumerate(docs):
    tf = dict.fromkeys(unique_words, 0)
    for word in doc:
      if word in tf.keys():
        tf[word] += 1
    tfs[i]=list(tf.values())
  return sparse.csr_matrix(tfs)

"""#**get_ntf**"""

def get_ntf(tfs):
  a=0.4
  count_vectors_inf=np.where(tfs.toarray()==0,float('inf'),tfs.toarray())
  n_tfs=np.where(count_vectors_inf==float('inf'),a,a+(1-a)*tfs.toarray()/np.max(tfs.toarray(),axis=1).reshape(-1,1))
  return n_tfs

"""#**Get IDF**"""

def get_idf(tfs,docs):
  df=np.sum(np.where(tfs.toarray()>=1,1,0),axis=0)
  idf=1+np.log(len(docs)/df).reshape(1,-1)
  return idf

"""#**TF-IDF**"""

def get_tf_idf(n_tfs,idf):
  ntf_idf=(n_tfs*idf).astype(np.float32)
  return ntf_idf

def load_data(filepath):
  temp_df=pd.read_csv(filepath)
  temp_df = temp_df[temp_df['text'].notna()]
  df=pd.DataFrame({'text': temp_df['text'].astype(str), 'topic':temp_df['topic'].astype(str)})
  # return df.iloc[35000:35500]
  return df

"""#**Main**"""

def main():
  start = time.time()
  filepath='/content/drive/MyDrive/Data Mining/reddit_data.csv'
  df=load_data(filepath)
  #process data
  docs,topics=preprocessing(df)
  t,c=np.unique(topics,  return_counts=True)
  c_sort_ind = np.argsort(-c)
  t=t[c_sort_ind]

  print(len(docs))
  # word freq
  freq=get_word_freq(docs)
  #unique word based on zif's law
  unique_words=get_unique_words2(freq,50,500)
  print(len(unique_words))
  #tfs (matrix)
  tfs=get_tf(docs,unique_words)
  # Maximum tf normalization
  n_tfs=get_ntf(tfs)
  #idf
  idf=get_idf(tfs,docs)
  #tf-idf
  ntf_idf=get_tf_idf(n_tfs,idf)
  del tfs,n_tfs,idf
  gc.collect()
  #PCA
  n_component=12
  ntf_idf_reduced,eigen_basis = PCA(ntf_idf,n_component)
  r, c = ntf_idf_reduced.shape
  #kmeans
  K=5
  centroids, cluster_affiliation, J, min_distance, min_distance_index, clutser_point_count=kmeans(ntf_idf_reduced, r, c, K)

  print('J: ',J)

  db= db_index(centroids, clutser_point_count, cluster_affiliation, min_distance, K)
  print('Davies–Bouldin index: ',db)

  dunn= dunn_index(centroids, clutser_point_count, cluster_affiliation, min_distance, K)
  print('Dunn index: ', dunn)


  plot_data(ntf_idf_reduced,cluster_affiliation,centroids,100)


  print('Duration: %s' % (time.time() - start))
if __name__ == "__main__":
  main()

"""#**Text Data**"""

def main():
  start = time.time()
  filepath='/content/drive/MyDrive/Data Mining/reddit_data.csv'
  df=load_data(filepath)
  #process data
  docs,topics=preprocessing(df)
  t,c=np.unique(topics,  return_counts=True)
  c_sort_ind = np.argsort(-c)
  t=t[c_sort_ind]

  print(len(docs))
  # word freq
  freq=get_word_freq(docs)
  #unique word based on zif's law
  unique_words=get_unique_words(freq,50,500)
  print(len(unique_words))
  #tfs (matrix)
  tfs=get_tf(docs,unique_words)
  # Maximum tf normalization
  n_tfs=get_ntf(tfs)
  #idf
  idf=get_idf(tfs,docs)
  #tf-idf
  ntf_idf=get_tf_idf(n_tfs,idf)
  del tfs,n_tfs,idf
  gc.collect()
  r, c = ntf_idf.shape
  #kmeans
  K=5
  centroids, cluster_affiliation, J, min_distance, min_distance_index, clutser_point_count=kmeans(ntf_idf, r, c, K)

  print('J: ',J)

  db= db_index(centroids, clutser_point_count, cluster_affiliation, min_distance, K)
  print('Davies–Bouldin index: ',db)

  dunn= dunn_index(centroids, clutser_point_count, cluster_affiliation, min_distance, K)
  print('Dunn index: ', dunn)


  print('Duration: %s' % (time.time() - start))
if __name__ == "__main__":
  main()

from sklearn.model_selection import train_test_split
def splitData(X, y):
  X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.30, random_state=42)
  return X_train, X_test, y_train, y_test

"""#**3**"""

# from sklearn.svm import SVC
# from sklearn.model_selection import train_test_split
# from keras.datasets import mnist
# from sklearn.metrics import f1_score
# from sklearn.metrics import confusion_matrix
# from sklearn.metrics import accuracy_score
# from sklearn.metrics import confusion_matrix
# import numpy as np

def loadall():
    (X_train, Y_train), (X_test, Y_test) = mnist.load_data()
    h_train,r_train,c_train=X_train.shape
    X_train=X_train.reshape(h_train,-1)/255.0
    h_test,r_test,c_test=X_test.shape
    X_test=X_test.reshape(h_test,-1)/255.0
    return X_train,Y_train,X_test,Y_test

def preprocessTestData(X_test,eigen_basis):
  A_X_test = X_test - np.mean(X_test,axis=0)
  reduced_X_test = np.dot(eigen_basis.T,A_X_test.T).T
  return reduced_X_test

def svc_clf(X,y,X_test,y_test):
    svc = SVC(kernel='linear')
    svc.fit(X,y)
    y_pred = svc.predict(X_test)

    f1score = f1_score(y_test,y_pred,average='macro')
    accuracy = accuracy_score(y_test,y_pred)
    print(classification_report(y_test, y_pred))
    print("F1 score: ",f1score)
    print('Accuracy: ',accuracy)
    print("Confusion matrix: \n",confusion_matrix(y_test, y_pred))

def main():
  start = time.time()
  filepath='/content/drive/MyDrive/Data Mining/reddit_data.csv'
  df=load_data(filepath)
  #process data
  docs,topics=preprocessing(df)

  docs, docs_test, topics, topics_test = splitData(docs, topics)
  #Full Dimension
  print("For Full Dimension: ")
  svc_clf(docs,topics,docs_test,topics_test)

  #Reduced Dimension
  num_component = 12
  docs_train_reduced,eigen_basis = PCA(docs,num_component)
  docs_test_reduced = preprocessTestData(docs_test,eigen_basis)
  print("For Reduced Dimension: ")
  svc_clf(docs_train_reduced,topics,docs_test_reduced,topics_test)


if __name__=='__main__':
    main()