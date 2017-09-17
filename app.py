from flask import Flask, render_template, request, redirect
import io
import csv
import numpy as np
import sys
import kmeans as kn
app = Flask(__name__)

@app.route('/')
def main():
	return redirect('/index')

@app.route('/index',methods=['GET'])
def index():
   # page for upload csv data and number of cluster
   return render_template('index.html')
	
@app.route('/result', methods = ['POST'])
def result():
   if request.method == 'POST':
      # ------------------------
      # load in input data
      # if error, output error.html
      # get number of cluster
      try:
         c_cnt=int(request.form['c_cnt'])
         method=int(request.form['method'])
         n_init=int(request.form['n_init'])

      except ValueError:
         error_msg='Wrong input for the number of clusters, initialization method or number of runs.'
         return render_template('error.html',error_msg=error_msg)

      # get the vector data
      csvfile = io.TextIOWrapper(request.files['file'].stream, encoding='gbk')
      reader = csv.reader(csvfile)
      X=np.array([[float(x) for x in line] for line in reader])

      if X.shape[0]==0:
         error_msg="No node data has been uploaded."
         return render_template('error.html',error_msg=error_msg)

      if X.shape[0]<c_cnt:
         error_msg="The number of cluster (k) is bigger than the number of vectors. Try a smaller k."
         return render_template('error.html',error_msg=error_msg)

      # -----------------
      # clustering all X
      kmeans=kn.KMeans(c_cnt,method=method,n_init=n_init)
      kmeans.fit(X)

      # ------------------
      # output results
      # the number of nodes for each cluster
      c_node_num=np.array([len(nodes) for nodes in kmeans.clusters.nodes])
      
      # the ordered cluster center based on the number of nodes
      centers=np.array([x for _, x in sorted(zip(c_node_num,kmeans.clusters.coords), key=lambda pair: pair[0])])
      centers=np.round(centers,1)
      centers=[', '.join(center.astype(str)) for center in centers]
      # sorted node number for each cluster
      c_node_num=','.join(sorted(c_node_num.astype(str)))
      return render_template('result.html',
         c_cnt=c_cnt,c_node_num=c_node_num,centers=centers,node_num=X.shape[0])
		
if __name__ == '__main__':
   try:
      app.run(debug = True,port=int(sys.argv[1]))
   except PermissionError:
      print('Permission Error! Try different port number, maybe >5000')