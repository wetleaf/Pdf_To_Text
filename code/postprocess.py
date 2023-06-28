import numpy as np

class PostProcess():

    #initalization
    def __init__(self,pageshape):
        
        self.shape = pageshape  # h,w

    # process(sort,removing duplicate etc.) the horizontal/vertical lines in the page
    def sort_by_index(self,lines,index):
        
        if not len(lines):
            return np.array([[0,0,0,0],[self.shape[1],self.shape[0],0,0]])
        
        lines = np.insert(lines,0,[[0,0,0,0]],axis=0)
        lines = np.append(lines,[[self.shape[1],self.shape[0],0,0]],axis=0)
        lines = np.unique(lines,axis=0)
        lines = lines[np.argsort(lines[:,index])]

        return lines
    
    # get the segment (segment are separated by horizontal lines)
    def get_segment(self,high,low,texts):
        segment = []
        remain = []
        for text in texts:
                if text[1][1] < high  and text[1][1] > low:
                    segment.append(text)
                else:
                    remain.append(text)
        
        return segment,remain

    # get the cluster (cluster are separated by vertical lines)
    def get_cluster(self,high,low,texts):
        cluster = []
        remain = []
        for text in texts:
                if text[1][0] < high  and text[1][0] > low:
                    cluster.append(text)
                else:
                    remain.append(text)
        
        return cluster,remain
    
    # arrange the text in form of lines
    def arrange_in_line(self,texts,horlines,verlines):

        lines = []
        remain = texts.copy()
        horlines = self.sort_by_index(horlines,1)
        verlines = self.sort_by_index(verlines,0)


        # for every segment
        for horidx in range(1,len(horlines)):
            

            y_upper = horlines[horidx-1][1]
            y_lower = horlines[horidx][1]
            segment,remain = self.get_segment(y_lower,y_upper,remain)
                 
            if segment:

                # for every cluster
                for veridx in range(1,len(verlines)):
                    
                    x_upper = verlines[veridx-1][0]
                    x_lower = verlines[veridx][0]
                    cluster,segment = self.get_cluster(x_lower,x_upper,segment)
                    
                    if cluster:

                        # sort the cluster by y index
                        
                        cluster = np.array(cluster,dtype=object)

                        cluster = cluster[np.argsort(np.stack(np.array(cluster[:,1]))[:,1])]
                        
                        # get the first word
                        line = [cluster[0]]

                        # process every word in the cluster if in same line, keep adding in the line else append line in lines and reinitailize the line
                        
                        for idx in range(1,len(cluster)):
                            
                            text = cluster[idx]
                            
                            if self.sameline(cluster[idx-1][1],text[1]):
                                line.append(text)
                            else:
                                line = np.array(line)
                                line = line[np.argsort(np.stack(np.array(line[:,1]))[:,0])]
                                lines.append(line)
                                line = line.copy()
                                line = [text]
                        
                        line = np.array(line)
                        line = line[np.argsort(np.stack(np.array(line[:,1]))[:,0])]
                        lines.append(line)
        
        
        return lines

    # check whether two words are in same line
    def sameline(self,box1,box2):

        l =  max(box1[1]+box1[3],box2[1]+box2[3]) -min(box1[1],box2[1])
        if ((box1[3]+box2[3])/l > 1.1):
            return True
        else:
            return False


    