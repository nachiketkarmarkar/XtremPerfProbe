import sys,time,json,StringIO
import xtremXenvLib
import xtremXmsLib
import xtremOperationsLib
import threading,csv

# Thread class that collects CPU utilization on all X-ENVs across all X-bricks via XMS
class collectXenvPerfThread(threading.Thread):

    def __init__(self, name, counter, samplePeriod, ip, user, pwd):
        threading.Thread.__init__(self)
        self.name=name
        self.samplePeriod=samplePeriod
        self.ip = ip
        self.user = user
        self.counter = counter
        self.pwd = pwd
        self.xenvPerf={}
        self.threadStatus = "running"
        self.file_handler = open("xenvPerfStats.csv","wb")
        self.writer = csv.writer(self.file_handler,dialect='excel')
        self.headerFlag = 0

    def run(self):
        print "Starting: %s" % (self.name)
        # self.collectXenvPerf()
        while self.counter > 0:
            self.collectXenvPerf()
            time.sleep(self.samplePeriod)
            self.counter-=1
            if self.threadStatus == "finished":
                break
        self.threadStatus = "finished"
        self.file_handler.close()
        print "Finished collecting Xenv stats"

    def recordStats(self,keys):
        currentStats = []
        for key in keys:
            currentStats.append(self.xenvPerf[key])
        self.writer.writerow(currentStats)

    def collectXenvPerf(self):
        output = xtremXenvLib.getXenvs(self.ip,self.user,self.pwd)
        # print output
        for xenv in output['xenvs']:
            if not xenv['name'] in self.xenvPerf:
                self.xenvPerf[str(xenv['name'])]=[]
                self.xenvPerf[str(xenv['name'])] = xtremXenvLib.getXenvUtil(self.ip,xenv['name'],self.user,self.pwd)
            else:
                self.xenvPerf[xenv['name']] = xtremXenvLib.getXenvUtil(self.ip,xenv['name'],self.user,self.pwd)
        # print self.xenvPerf
        keys = self.xenvPerf.keys()
        if self.headerFlag == 0:
            self.writer.writerow(keys)
            self.recordStats(keys)
            self.headerFlag+=1
        else:
            self.recordStats(keys)            

class collectXmsPerfThread(threading.Thread):

    def __init__(self, name, counter, samplePeriod, ip, user, pwd):
        threading.Thread.__init__(self)
        self.name=name
        self.counter=counter
        self.samplePeriod=samplePeriod
        self.ip = ip
        self.user = user
        self.pwd = pwd
        self.xmsPerf={'read-latency': [],'write-latency': [],\
                      'read-bandwidth':[],'write-bandwidth':[],'bandwidth':[],\
                      'read-iops':[],'write-iops':[],'iops':[],\
                      'dedup-ratio':[],'compression-factor':[]}
        self.threadStatus = "running"
        self.file_handler = open("xmsPerfStats.csv","wb")
        self.writer = csv.writer(self.file_handler,dialect='excel')
        self.writer.writerow(self.xmsPerf.keys())

    def run(self):
        print "Starting: %s" % (self.name)
        #self.collectXmsPerf()
        while self.counter > 0:
            self.collectXmsPerf()
            time.sleep(self.samplePeriod)
            self.counter-=1
            if self.threadStatus == "finished":
                break
        self.threadStatus = "finished"
        self.file_handler.close()
        print "Finished collecting XMS stats"

    def recordStats(self,keys):
        currentStats = []
        for key in keys:
            currentStats.append(self.xmsPerf[key])
        self.writer.writerow(currentStats)

    def collectXmsPerf(self):
            output = xtremXmsLib.getXms(self.ip,self.user,self.pwd)
            self.xmsPerf['read-latency'] = str(output['content']['rd-latency'])
            self.xmsPerf['write-latency'] = str(output['content']['wr-latency'])
            self.xmsPerf['read-bandwidth'] = int(output['content']['rd-bw'])/1000
            self.xmsPerf['write-bandwidth'] = int(output['content']['wr-bw'])/1000
            self.xmsPerf['bandwidth'] = int(output['content']['bw'])/1000
            self.xmsPerf['read-iops'] = str(output['content']['rd-iops'])
            self.xmsPerf['write-iops'] = str(output['content']['wr-iops'])
            self.xmsPerf['iops'] = str(output['content']['iops'])
            self.xmsPerf['dedup-ratio'] = xtremXmsLib.getCurrentDedupRatio(self.ip,self.user,self.pwd)
            self.xmsPerf['compression-factor'] = xtremXmsLib.getCurrentCompressionFactor(self.ip,self.user,self.pwd)
            self.recordStats(self.xmsPerf.keys())
            #print self.xmsPerf

class collectVolPerfThread(threading.Thread):

    def __init__(self, vol, counter, samplePeriod, ip, user, pwd):
        threading.Thread.__init__(self)
        self.vol=vol
        self.counter=counter
        self.samplePeriod=samplePeriod
        self.ip = ip
        self.user = user
        self.pwd = pwd
        self.volPerf={'read-latency': [],'write-latency': [],\
                      'read-bandwidth':[],'write-bandwidth':[],'bandwidth':[],\
                      'read-iops':[],'write-iops':[],'iops':[]}
        self.threadStatus = "running"
        self.file_handler = open("%s.csv" %(self.vol),"wb")
        self.writer = csv.writer(self.file_handler,dialect='excel')
        self.writer.writerow(self.volPerf.keys())

    def run(self):
        print "Starting Performance metric collection for : %s" % (self.vol)
        #self.collectXmsPerf()
        while self.counter > 0:
            self.collectVolPerf()
            time.sleep(self.samplePeriod)
            self.counter-=1
            if self.threadStatus == "finished":
                break
        self.threadStatus = "finished"
        self.file_handler.close()
        print "Finished collecting stats for %s" % (self.vol)

    def recordStats(self,keys):
        currentStats = []
        for key in keys:
            currentStats.append(self.volPerf[key])
        self.writer.writerow(currentStats)

    def collectVolPerf(self):
            output = xtremOperationsLib.getVolumeDetails(self.ip,self.user,self.pwd,str(self.vol))
            self.volPerf['read-latency'] = str(output['content']['rd-latency'])
            self.volPerf['write-latency'] = str(output['content']['wr-latency'])
            self.volPerf['read-bandwidth'] = int(output['content']['rd-bw'])/1000
            self.volPerf['write-bandwidth'] = int(output['content']['wr-bw'])/1000
            self.volPerf['bandwidth'] = int(output['content']['bw'])/1000
            self.volPerf['read-iops'] = str(output['content']['rd-iops'])
            self.volPerf['write-iops'] = str(output['content']['wr-iops'])
            self.volPerf['iops'] = str(output['content']['iops'])
            self.recordStats(self.volPerf.keys())
            #print self.xmsPerf

def main():
    xenvPerfThread = collectXenvPerfThread("XenvPerfCollector", 30, 5)
    xenvPerfThread.start()
    xmsPerfThread = collectXmsPerfThread("XmsPerfCollector", 30, 5)
    xmsPerfThread.start()
    while xenvPerfThread.threadStatus == "running" or xmsPerfThread.threadStatus == "running":
        time.sleep(5)
    xtremPerfStats = dict(xenvPerfThread.xenvPerf)
    print xtremPerfStats.keys()
    xtremPerfStats.update(xmsPerfThread.xmsPerf)
    print xtremPerfStats.keys()
    
    file_handler = open("xtremPerfStats.csv","wb")
    writer = csv.writer(file_handler,dialect='excel')
    keys = xtremPerfStats.keys()
    writer.writerow(keys)
    transposed = []
    for key in xtremPerfStats.keys():
        transposed.append(xtremPerfStats[key])
    writer.writerows(zip(*transposed))
    
    
    
if __name__ == '__main__':
    main()

  
#print xtremXenvLib.getXenvUtil(ip,xenv['name'],user,pwd)