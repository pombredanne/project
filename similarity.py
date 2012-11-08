# given the file name of the term document matrix
# load it into memory, compute a tf-idf matrix, and then
# compute pairwise similarity based on normalized dot product (cosine similarity)
import math
import os
from numpy import *
import codecs
import clusters

def load_tdf(tdf_name="out/tdf.txt"):
    """load a term document matrix from a tab-delimited text file, generated by get_counts.py"""
    lines = [line for line in file(tdf_name)]
    # first line is column titles
    colnames=lines[0].strip().split('\t')[1:]
    rownames=[]
    data=[]
    for line in lines[1:]:
        p=line.strip().split('\t')
        # rownames is the first in each row
        rownames.append(p[0])
        # data is in the remainder of each row
        data.append([float(x) for x in p[1:]])
    return rownames,colnames,matrix(data)
    
def compute_idf(tdf):
    """compute the inverse document frequency of each word from its term document matrix"""
    idf=[]
    total_documents = shape(tdf)[1]
    term_doc_inc = where(tdf>0,1,0) # creates a term-document incidence matrix
    doc_freq = term_doc_inc.sum(axis=0)
    idf = doc_freq/float(total_documents)
    for i in range(total_documents):
        if idf[0,i]==0:
            idf[0,i]=1.0
        else:
            idf[0,i] = 1.0+math.log(idf[0,i])
    return idf
    
def compute_tf_idf_matrix(tdf,idf):
    """Convert a term document matrix into a tf-idf matrix given the matrix and the idf"""
    tdf=array(tdf)
    idf=array(idf)
    for i in range(len(tdf)):
        tdf[i]=tdf[i]*idf
    return matrix(tdf)          

def normalize_tf_idf(tfidf):
    """Convert a matrix so that its rows have norm 1, so we can efficiently compute similarity, may be unnecessary?"""
    for row in range(shape(tfidf)[0]):
        tfidf[row] = tfidf[row]/linalg.norm(tfidf[row])
    return tfidf
        
def compute_similarity(v1,v2):
    """compute cosine similarity between two vectors, assumes they have been normalized by tf-idf"""
    v1=matrix(v1)
    v2=matrix(v2)
    try:
        res= inner(v1,v2)/linalg.norm(v1)/linalg.norm(v2)
    except ZeroDivisionError:
        res=1.0
    return float(res)

def compute_similarity_normalized(v1,v2):
    """compute cosine similarity between two vectors, assumes they have been normalized by tf-idf and normalized so that norm=1"""
    v1=matrix(v1)
    v2=matrix(v2)
    try:
        res= inner(v1,v2)
    except ZeroDivisionError:
        res=1.0
    return float(res)
    
def compute_similarity_matrix(rownames,tfidf):
    """compute a similarity matrix of documents (blogs) given names and tfidf"""
    # initialize to 0
    sim_mat = [[0.0 for i in range(len(rownames))] for j in range(len(rownames))]
    total=str(len(rownames)*(len(rownames)-1)/2)
    k=0
    for i in range(len(rownames)):
        sim_mat[i][i]=1.0 # a blog is completely similar to itself
        for j in range(i+1,len(rownames)):
            # so, this matrix is symmetric because similarity is symmetric
            sim_mat[i][j] = compute_similarity(tfidf[i],tfidf[j])
            sim_mat[j][i] = sim_mat[i][j]
            k+=1
            if k%1000==0:
                print " --> Completed " + str(k) + " of " + total
    print " --> Similarity matrix computation completed."        
    return sim_mat
    
def write_similarity(sim,names,filename="similarity.txt"):
    """ write out similarity matrix to tab-separated text file """
    out = codecs.open(os.path.join(os.getcwd(), 'out', filename), 'w',encoding='iso-8859-1')
    out.write('Blog')
    for blog in names:
        out.write('\t%s' % blog)
    i=0
    out.write('\n')
    for blog in names:
        out.write(blog)
        for j in range(len(names)):
            out.write('\t%f' % sim[i][j])
        out.write('\n')
        i+=1
    return
    
def main():
    print "Loading term document matrix"
    rownames,colnames,counts=load_tdf("out/tdf.txt")
    print "Computing IDF"
    idf=compute_idf(counts)
    print "Computing TF-IDF matrix"
    tfidf=compute_tf_idf_matrix(counts,idf)
    n_clus=15
    print "Computing " + str(n_clus) + " clusters"
    blog_clus=clusters.kcluster(tfidf,distance=compute_similarity_normalized,k=n_clus)
    f = open("out/blog_clus.txt",'w')
    for i in range(len(blog_clus)):
        for j in range(len(blog_clus[i])):
            f.write(str(i) + "\t" + rownames[blog_clus[i][j]] + "\n")
    f.close()        
    #print "Computing similarity matrix"
    #sim=compute_similarity_matrix(rownames,tfidf)
    #print "Writing similarity matrix"
    #write_similarity(sim,rownames,filename="similarity.txt")
    
if __name__=="__main__": main()    