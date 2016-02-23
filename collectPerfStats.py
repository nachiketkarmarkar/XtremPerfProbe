from pyVim.connect import Connect, Disconnect
from pyVmomi import vim
import time, getopt, sys, ssl
import threading,time,csv
import collectVcPerf
import collectXtremPerf
import generatePlots
import numpy as np
import matplotlib.pyplot as plot
import re

def handleKill(xenvPerfThread,xmsPerfThread,esxHostPerfThreads,volPerfThreads):
    print "Received Ctrl+C Signal ... "
    stopEsxThreads(esxHostPerfThreads)
    stopVolPerfThreads(volPerfThreads)
    if xenvPerfThread or xmsPerfThread:
        print "Stopping XENV Thread ..."
        xenvPerfThread.threadStatus = "finished"
        print "Stopping XMS Thread"
        xmsPerfThread.threadStatus = "finished"
        processAndPlotXtremIO(xenvPerfThread,xmsPerfThread)

def startXenvPerfCollect(counter, samplingRate, xmsip, xmsuser, xmspwd):
    xenvPerfThread = collectXtremPerf.collectXenvPerfThread("XenvPerfCollector", counter, int(samplingRate), xmsip, xmsuser, xmspwd)
    xmsPerfThread = collectXtremPerf.collectXmsPerfThread("XmsPerfCollector", counter, int(samplingRate), xmsip, xmsuser, xmspwd)
    xenvPerfThread.start()
    xmsPerfThread.start()
    return xmsPerfThread,xenvPerfThread

def startVolumePerfThreads(counter, samplingRate, volumes, xmsip, xmsuser, xmspwd):
    volPerfThreads = []
    for vol in volumes:
        volThread = collectXtremPerf.collectVolPerfThread(vol, counter, int(samplingRate), xmsip, xmsuser, xmspwd)
        volThread.start()
        volPerfThreads.append(volThread)
    return volPerfThreads

def getVmwServiceContent(vcip, vcuser, vcpwd):
    unverified_context=ssl._create_unverified_context
    ssl._create_default_https_context=unverified_context
    si=Connect(host=vcip,port=443,user=vcuser,pwd=vcpwd)
    return si.RetrieveContent()

def startEsxPerfCollect(vcip, vcuser, vcpwd, hostnames, samplingRate):
    print vcip+"    "+vcuser+"      "+vcpwd
    content=getVmwServiceContent(vcip, vcuser, vcpwd)
    datacenter=content.rootFolder.childEntity[0]
    hostList=datacenter.hostFolder.childEntity
    esxHostPerfThreads = []
    esxHosts = []
    for host in hostList:
        for esx in host.host:
            esxHosts.append(esx)
    for server in esxHosts:
        for serverName in hostnames:
            if re.search(serverName, server.name):
                print "Found: "+serverName+" matched with "+server.name
                esxHostThread = collectVcPerf.collectVcPerfThread("ESXPerfThread",server,content,samplingRate)
                esxHostPerfThreads.append(esxHostThread)
                esxHostThread.start()
    return esxHostPerfThreads

def stopEsxThreads(esxHostPerfThreads):
    if not esxHostPerfThreads == None:
        for esxThread in esxHostPerfThreads:
            print "Stopping ESX thread..."
            esxThread.threadStatus = "Halt"

def stopVolPerfThreads(volPerfThreads):
    if not volPerfThreads == None:
        for volThread in volPerfThreads:
            print "Stopping volume perfmon thread..."
            volThread.threadStatus = "finished"

def processAndPlotEsx(vcip, vcuser, vcpwd, hostlist):
    content = getVmwServiceContent(vcip, vcuser, vcpwd)
    datacenter=content.rootFolder.childEntity[0]
    clusters=datacenter.hostFolder.childEntity
    for hosts in clusters:
        for host in hosts.host:
            if host.name in hostlist:
                print "Generating plots for %s" %(host.name)
                storageHba= []
                adapters=host.config.storageDevice.hostBusAdapter
                for hba in adapters:
                    if type(hba) is vim.host.FibreChannelHba:
                        storageHba.append(hba.device)
                generatePlots.drawEsxCharts(host.name,storageHba)

def usage():
    print "Usage: collectPerfStats.py -<option>  <parameter>"
    print "    "
    print "                      -i     <XMS Server IP>                        or            --xmsip     <XMS Server IP>"
    print "                      -u     <XMS username>                         or            --xmsuser   <XMS username>*"                    
    print "                      -p     <XMS password>                         or            --xmspwd    <XMS password>*"
    print "                      -v     <vCenter Server IP>                     or            --vcip      <vCenter Server IP>"                
    print "                      -l     <vCenter server username>               or            --vcuser    <vCenter server username>"
    print "                      -c     <vCenter Server password>               or            --vcpwd     <vCenter Server password>"
    print "                      -d     <duration>*                             or            --duration  <duration>"
    print "                      -e     <comma separated FQDN of ESX hosts>     or            --hostnames <comma separated FQDN of ESX hosts>"
    print "                      -x     <comma separated XtremIO volume names   or            --volumes   <comma separated XtremIO volume names"    
    print "                      -s     <sampling frequency in seconds>*        or            --sampling  <sampling frequency in seconds>"
    print "    "
    print "'*' Indicates essential parameter and has to be given. Make sure sampling frequency is more than 5 seconds"
    print "    "
    
def main():
    xmsip=xmsuser=xmspwd=vcip=vcuser=vcpwd=None
    listOfHosts=None
    listOfVols=None
    samplingRate=None
    duration=None
    noVsphereStatsFlag = 0
    noXtremStatsFlag = 0
    hostnames = None
    xmsPerfThread = None
    xenvPerfThread = None
    esxHostPerfThreads = None
    volPerfThreads = None
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hi:u:p:v:l:c:d:e:x:s:", \
                                   ["help", "xmsip=","xmsuser=","xmspwd=","vcip=","vcuser=","vcpwd=","duration=","hostnames=","volumes","sampling="])
    except getopt.GetoptError:
        usage()
        sys.exit(1)
    for opt, arg in opts:
        # print opt+":"+arg
        if opt in ("-h", "--help"):
            usage()
            sys.exit(1)
        if opt in ("-i", "--xmsip"):
            xmsip = str(arg)
        if opt in ("-u", "--xmsuser"):
            xmsuser = str(arg)
        if opt in ("-p", "--xmspwd"):
            xmspwd = str(arg)
        if opt in ("-v", "--vcip"):
            vcip = str(arg)
        if opt in ("-l", "--vcuser"):
            vcuser = str(arg)
        if opt in ("-c", "--vcpwd"):
            vcpwd = str(arg)
        if opt in ("-d", "--duration"):
            duration = int(arg)
        if opt in ("-e", "--hostnames"):
            listOfHosts = str(arg)
        if opt in ("-x", "--volumes"):
            listOfVols = str(arg)
        if opt in ("-s", "--sampling"):
            samplingRate = int(arg)

    try:
        if duration == None or duration == "" or samplingRate == None or samplingRate == "":
            print "ABORT: duration and sampling rate are mandatory"
            usage()
            sys.exit(2)
        counter = duration/samplingRate
        if xmsip == None or xmsip == "" or xmsuser == None or xmsuser == "" or xmspwd == None or xmspwd == "" or \
                  int(duration) == 0 or int(samplingRate) == None or int(samplingRate) < 5:
            print "WARNING: XMS IP address, XMS username or XMS password or hostlist is not provided, Checking vSphere arguments"
        else:
            noXtremStatsFlag = 1
            xmsPerfThread,xenvPerfThread = startXenvPerfCollect(counter,samplingRate,xmsip,xmsuser,xmspwd)
        
        if vcip == None or vcuser == None or vcpwd == None or listOfHosts == None or vcip == "" or vcuser == "" or vcpwd == "" or listOfHosts == "":
            print "WARNING: VC IP address, VC username, VC password or hostlist is not provided, only XtremIO stats will be collected"
        else:
            noVsphereStatsFlag = 1
            hostnames = listOfHosts.split(',')
            esxHostPerfThreads = startEsxPerfCollect(vcip, vcuser, vcpwd, hostnames, samplingRate)
        if listOfVols:
            print "Collecting stats for specified volumes"
            volumes = listOfVols.split(',')
            print volumes
            volPerfThreads = startVolumePerfThreads(counter, samplingRate, volumes, xmsip, xmsuser, xmspwd)
        if not noVsphereStatsFlag and not noXtremStatsFlag:
            print "ABORT: Incomplete args provided for vSphere and/or XtremIO stats collection"
            usage()
            sys.exit(2)
        timerStart = time.time()
        if noXtremStatsFlag:
            while xenvPerfThread.threadStatus != "finished" or xmsPerfThread.threadStatus != "finished":
                time.sleep(1)
        else:
            while int(counter) > 0:
                time.sleep(int(samplingRate))
                counter-=1
        if noVsphereStatsFlag:
            stopEsxThreads(esxHostPerfThreads)
            processAndPlotEsx(vcip, vcuser, vcpwd, hostnames)
        if noXtremStatsFlag:
            generatePlots.drawXtremIOCharts()
        if volPerfThreads:
            for volume in volumes:  
                generatePlots.drawVolPerfCharts(volume)
    except KeyboardInterrupt:
        print "Ctrl+C recevied ..."
        handleKill(xenvPerfThread,xmsPerfThread,esxHostPerfThreads,volPerfThreads)
if __name__ == '__main__':
    main()