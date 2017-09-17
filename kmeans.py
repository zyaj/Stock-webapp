import numpy as np
import random
#####################
# class: clusters(c_cnt,coords)
# init: number of clusters
#       vector array for the locations for all clusters
# usage: store clusters
# para: c_cnt=number of cluster
#       coords=vector array for the initial location of cluster centers
# Yun Zhang 09/16/2017
#####################
class clusters():
    
    # initialization
    def __init__(self,c_cnt,coords):
        self.c_cnt=c_cnt        
        self.coords=coords
        self.init_coords=coords.copy()
        self.pre_coords=None
        self.fit=False
        self.nodes=[set() for k in range(c_cnt)]
    
    # eliminate all nodes index for each cluster
    def reset_nodes(self):
        self.nodes=[set() for k in range(c_cnt)]
    
    # add a node index for c_id cluster
    def push(self,node_id,c_id):
        self.nodes[c_id].add(node_id)
    
    # get all node data for cluster c_id
    def nodes_data(self,X,c_id):
        return X[list(self.nodes[c_id])]
    
    # apply mean to update cluster centers
    def update_coord(self,X):
        if not self.fit:
            self.fit=True
        self.pre_coords=self.coords
        for i,nodes in enumerate(self.nodes):
            self.coords[i]=np.mean(X[list(nodes)],axis=0)
    
    # check convergence
    def is_converged(self,tol=1e-3):
        if self.fit:
            if max(np.sum((self.pre_coords-self.coords)**2,axis=1))<tol:
                return True
        return False
    
    # assign nodes to the closed cluster center
    def assign_nodes(self,X):
        # get number of node
        node_cnt=X.shape[0]
        # the distance matrix between nodes and cluster center
        dist_mat=np.sum((X-self.coords[0])**2,axis=1).reshape(node_cnt,1)
        # loop over all the left cluster
        for i in range(1,self.c_cnt):
            dist_mat=np.concatenate((dist_mat,
                                     np.sum((X-self.coords[i])**2,axis=1).reshape(node_cnt,1)),
                                    axis=1)
        # initial the nodes assignment list
        self.nodes=[set() for k in range(self.c_cnt)]
        # assign nodes to the cluster with min distance
        for i,ind in enumerate(dist_mat.argmin(axis=1)):
            self.nodes[ind].add(i)
    
    # predict cluster for nodes array X       
    def predict(self,X):
        # get number of node
        node_cnt=X.shape[0]
        # the distance matrix between nodes and cluster center
        dist_mat=np.sum((X-self.coords[0])**2,axis=1).reshape(node_cnt,1)
        # loop over all the left cluster
        for i in range(1,self.c_cnt):
            dist_mat=np.concatenate((dist_mat,
                                     np.sum((X-self.coords[i])**2,axis=1).reshape(node_cnt,1)),
                                    axis=1)
        # initial the nodes assignment list
        nodes_c_id=[set() for k in range(self.c_cnt)]
        # assign nodes to the cluster with min distance
        for i,ind in enumerate(dist_mat.argmin(axis=1)):
            nodes_c_id[ind].add(i)
        return nodes_c_id,sum(np.min(dist_mat,axis=1))
    
    # output sum squared distance for train data
    def train_ss_dist(self,X):
        ss_dist=0
        for i,nodes in enumerate(self.nodes):
            ss_dist+=sum(np.sum((X[list(nodes)]-self.coords[i])**2,axis=1))
        return ss_dist


##############
# function: InitializeKmeans(X,c_cntmethod)
# input: the vection array for the location of all points
#        the number of clusters
#        initialization method
# usage: initialize the locations for all clusters
# para: method=0: random, method=1: kmeans++, method=2: kmeans||
#       l=oversample coefficient, r=the number of rounds for picking nodes for kmeans||
# Yun Zhang 09/16/2017
##############
def InitializeKmeans(X,c_cnt,method=1,l=0.5,r=5):
    
    # randomly pick initial cluster center
    if method==0:
        return X[random.sample(range(X.shape[0]),c_cnt)]
    
    # apply kmeans++ initialization
    if method==1:
        c_ind=list()
        node_cnt=X.shape[0]
        c_ind.append(random.randint(0,node_cnt-1))
        dist_mat=np.sum((X-X[c_ind[0]])**2,axis=1).reshape(node_cnt,1)
        while len(c_ind)<c_cnt:
            p=(np.min(dist_mat,axis=1))/sum(np.min(dist_mat,axis=1))
            c_ind.append(np.random.choice(range(node_cnt),p=p))
            #c_ind.append(p.argmax())
            tmp=np.sum((X-X[c_ind[-1]])**2,axis=1).reshape(node_cnt,1)
            dist_mat=np.concatenate((dist_mat,tmp),axis=1)
        return X[c_ind]
    
    # apply kmeans|| initialization
    if method==2:
        node_cnt=X.shape[0]
        # check efficiency
        if l*r*c_cnt>node_cnt:
            print('''Warning: The sampling clusters centers are more than the nodes,
            which may induce inefficiency.''')
        
        # start initialization
        c_ind=list()
        # randomly pick one node
        c_ind.append(random.randint(0,node_cnt-1))
        dist_mat=np.sum((X-X[c_ind[0]])**2,axis=1).reshape(node_cnt,1)
        rnd=0
        while len(c_ind)<c_cnt or rnd<r:
            # sample nodes based on oversample facor l*c_cnt
            p=l*c_cnt*(np.min(dist_mat,axis=1))/sum(np.min(dist_mat,axis=1))
            p_sample=np.random.uniform(size=node_cnt)
            for i in range(node_cnt):
                if p_sample[i]>p[i]:
                    c_ind.append(i)
            rnd+=1
        # now there are approximate r*l*c_cnt nodes
        # clustering them to get c_cnt clusters
        if len(c_ind)==c_cnt:
        	return X[c_ind]
        else:
        	k_sub_cluster=KMeans(c_cnt,method=1,n_init=10)
        	k_sub_cluster.fit(X[c_ind])
        	return k_sub_cluster.clusters.coords

####################
# class Kmeans(c_cnt,method)
# input: the number of clusters
#        the initialization method
# usage: build a Kmeans clustering classifier
#        and apply Lloyd's algorithm
# Yun Zhang 09/16/2017
####################
class KMeans():
    
    # initialize clustering classifier
    def __init__(self,c_cnt,method=2,tol=1e-3,n_init=50,max_iter=300):

        self.method=method
        self.c_cnt=c_cnt
        self.tol=1e-3
        self.clusters=None
        self.n_init=n_init
        self.max_iter=max_iter
    
    # train the classifer within train data X
    def fit(self,X):
        # apply Lloyd's algorithm
        for i in range(self.n_init):
            iter=0
            cluster_tmp=clusters(self.c_cnt,InitializeKmeans(X,self.c_cnt,self.method))
            while (not cluster_tmp.is_converged(self.tol)) and iter<self.max_iter:
                cluster_tmp.assign_nodes(X)
                cluster_tmp.update_coord(X)
            if i==0:
                self.clusters=cluster_tmp
            else:
                if self.clusters.train_ss_dist(X)>cluster_tmp.train_ss_dist(X):
                    self.clusters=cluster_tmp
    
    # predict clustering for input data
    def predict(self,X):
        return self.clusters.predict(X)