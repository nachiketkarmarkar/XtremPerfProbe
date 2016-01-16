from pyVim.connect import Connect, Disconnect
from pyVmomi import vim
import time
import threading,time

class collectVcPerfThread(threading.Thread):
    def __init__(self,name,host,content,samplingRate):
        threading.Thread.__init__(self)
        self.name = name
        self.host = host
        self.content = content
        self.samples = 1
        self.sampleSpread = 20
        #self.samplingInterval = self.samples*self.sampleSpread
        self.samplingInterval = samplingRate
        self.filename = "%s.csv" % (self.host.name)
        self.headerFlag = 0
        self.esxCounters = None
        self.fileHandle = None
        self.threadStatus = "Running"
        self.esxhost_counters_select = [
                          # CPU
                          {"metric" : "Utilization",  "group" : "CPU", "type" : "average", "instance" : ""},
                          # # Memory
                          {"metric" : "Usage",  "group" : "Memory", "type" : "average", "instance" : "*"},
                          {"metric" : "Active",  "group" : "Memory", "type" : "average", "instance" : "*"},
                          # Storage adapter
                          {"metric" : "Average read requests per second",  "group" : "Storage adapter", "type" : "average", "instance" : "*"},
                          {"metric" : "Average write requests per second",  "group" : "Storage adapter", "type" : "average", "instance" : "*"},
                          {"metric" : "Read rate",  "group" : "Storage adapter", "type" : "average", "instance" : "*"},
                          {"metric" : "Write rate",  "group" : "Storage adapter", "type" : "average", "instance" : "*"},
                          {"metric" : "Read latency",  "group" : "Storage adapter", "type" : "average", "instance" : "*"},
                          {"metric" : "Write latency",  "group" : "Storage adapter", "type" : "average", "instance" : "*"},
                          {"metric" : "Storage Adapter Queue Command Latency",  "group" : "Storage adapter", "type" : "average", "instance" : "*"},
                          {"metric" : "Storage Adapter Throughput Usage",  "group" : "Storage adapter", "type" : "average", "instance" : "*"},
                          # Disk
                          {"metric" : "Read rate",  "group" : "Disk", "type" : "average", "instance" : "*"},
                          {"metric" : "Write rate",  "group" : "Disk", "type" : "average", "instance" : "*"},
                          {"metric" : "Read latency",  "group" : "Disk", "type" : "average", "instance" : "*"},
                          {"metric" : "Write latency",  "group" : "Disk", "type" : "average", "instance" : "*"},
                          {"metric" : "Average read requests per second",  "group" : "Disk", "type" : "average", "instance" : "*"},
                          {"metric" : "Average write requests per second",  "group" : "Disk", "type" : "average", "instance" : "*"}
                         ]
    def run(self):
        print "Starting Threads to collect ESX perf data"
        print self.host.name
        self.collectVcPerf()
        timerStart = time.time()
        while True:
            if self.threadStatus == "Halt":
                break
            timeDiff = time.time() - timerStart
            if timeDiff >= self.sampleSpread:
                timerStart = time.time()
                self.collectVcPerf()
            time.sleep(1)
        print "Finished collecting ESX stats"

    def collectVcPerf(self):
        esxCounters = self.filterEsxCounters()
        querySpec = self.makeQuery(esxCounters)
        perfData = self.content.perfManager.QueryStats(querySpec)
        curedData = self.formatPerfData(perfData)
        # print curedData
        self.serializePerfData(curedData)
            
    def filterEsxCounters(self):
        esxCounters = {}
        for counter in self.content.perfManager.perfCounter:
            for i in range(0,len(self.esxhost_counters_select)):
                if counter.nameInfo.label == self.esxhost_counters_select[i]["metric"] and \
                    counter.groupInfo.label == self.esxhost_counters_select[i]["group"] and \
                    counter.rollupType == self.esxhost_counters_select[i]["type"]:
                        esxCounters[counter.key] = counter
        self.esxCounters = esxCounters
        return esxCounters

    def makeQuery(self, esxCounters):
        perfMetrics = []
        for key in esxCounters.keys():
            metricId = vim.PerformanceManager.MetricId()
            metricId.counterId = key
            if self.verifyCounterGroup(key) == "CPU":
                metricId.instance = ""
            else:
                metricId.instance = "*"
            perfMetrics.append(metricId)
        # print len(perfMetrics)
        querySpec = vim.PerformanceManager.QuerySpec()
        querySpec.entity = self.host
        querySpec.format = "csv"
        querySpec.maxSample = self.samples
        querySpec.intervalId = self.sampleSpread
        querySpec.metricId = perfMetrics
        return [querySpec]

    def formatPerfData(self,perfData):
        curedData = {}
        curedData[self.host.name] = {}
        if "timestamp" not in curedData[self.host.name].keys():
            curedData[self.host.name]["timestamp"] = {}
            curedData[self.host.name]["timestamp"]["0"] = []

        timestamps = perfData[0].sampleInfoCSV.split(",")
        timestamps = filter (lambda a: a != "20", timestamps)

        for i in range(len(timestamps)):
            curedData[self.host.name]["timestamp"]["0"].append(timestamps[i])

        for counter in perfData[0].value:
            counterId = counter.id.counterId
            instance = counter.id.instance
            values = counter.value.split(",")
            if counterId not in curedData[self.host.name].keys():
                curedData[self.host.name][counterId] = {}
            if instance not in curedData[self.host.name][counterId].keys():
                curedData[self.host.name][counterId][instance] = []
            
            for i in range(len(values)):
                if self.verifyCounterUnit(counterId):
                    values[i] = float(values[i])/100
                curedData[self.host.name][counterId][instance].append(values[i])
        
        return curedData

    def serializePerfData(self, curedData):
        if self.headerFlag == 0:
            self.fileHandle = open(self.filename, "w")
        else:
            self.fileHandle = open(self.filename, "a")
        if self.host.name not in curedData.keys():
            print "No performance data collected for the entity: %s" % self.host.name
        if self.headerFlag == 0:
            print >> self.fileHandle, "Timestamp,",
            # write the header
            ids = curedData[self.host.name].keys()
            ids.remove("timestamp")
            for id in ids:
                instances = curedData[self.host.name][id].keys()
                instances.sort()
                for instance in instances:
                    counter = self.esxCounters[id]
                    metric_str =  "%s-%s %s (%s) in %s" % \
                           (counter.groupInfo.label, instance, \
                            counter.nameInfo.label, counter.rollupType, \
                            counter.unitInfo.label)
                    print >> self.fileHandle, "%s," % (metric_str),
            print >> self.fileHandle, "\n",
            self.headerFlag = 1
        # write the samples
        firstentityname = curedData.keys()[0] 
        for count in range(0, len(curedData[firstentityname]["timestamp"]["0"])):
            print >>self.fileHandle, "%s," % curedData[firstentityname]["timestamp"]["0"][count],
            if self.host.name not in curedData.keys():
                print "No perf data collected for the entity: %s" % self.host.name

            ids = curedData[self.host.name].keys()
            ids.remove("timestamp")
            for id in ids:
                instances = curedData[self.host.name][id].keys()
                instances.sort()
                for instance in instances:
                    try:
                        print >> self.fileHandle, "%s," % curedData[self.host.name][id][instance][count],
                    except:
                        print >> self.fileHandle, "0,",
                        print "Data was not found for entity: %s, id: %s, instance: %s, count: %d" % (self.host.name, id, instance, count)
            print >> self.fileHandle, "\n",
        self.fileHandle.close()
        return

    def verifyCounterUnit(self, counterId):
        if counterId in self.esxCounters.keys():
            if self.esxCounters[counterId].unitInfo.label == "%":
                # print(self.esxCounters[counterId])
                return True
            else:
                return False
        else:
            return False

    def verifyCounterGroup(self, counterId):
        if counterId in self.esxCounters.keys():
            return self.esxCounters[counterId].groupInfo.label

def main():
    si=Connect(host="10.10.225.151",port=443,user="administrator@xtrem.vsphere",pwd="XtremIO123!")
    content=si.RetrieveContent()
    datacenter=content.rootFolder.childEntity[0]
    hostList=datacenter.hostFolder.childEntity
    for host in hostList:
        print host.host[0].name
    esxHostThread = collectVcPerfThread("TestThread",hostList[1].host[0],content)
    esxHostThread.start()
    time.sleep(300)
    esxHostThread.threadStatus = "Halt"
    print "stopping VC perfmon collector"
        

if __name__ == '__main__':
    main()