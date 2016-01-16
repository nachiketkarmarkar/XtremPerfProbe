import numpy as np
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plot
import matplotlib.pylab
from matplotlib.backends.backend_pdf import PdfPages
import re

def drawPlots(data,plotObj,name,yLabel,position):
    drawing = plotObj.add_subplot(position,1,position)
    drawing.set_ylabel(yLabel, fontsize=16)
    drawing.set_xlabel("Sample", fontsize=18)
    drawing.plot(data[name], label = name)
    drawing.legend(loc = 'upper center', bbox_to_anchor=(0.9, 1.128))
    # drawing.legend(loc = 'upper center')

    
def drawXtremIOCharts():
    xenvData = np.genfromtxt('xenvPerfStats.csv', dtype=float, delimiter=',', names=True)
    xmsData = np.genfromtxt('xmsPerfStats.csv', dtype=float, delimiter=',', names=True)
    plot.ioff()
    iops = plot.figure(figsize=(20,15))
    iops.suptitle("IOPs", fontsize=20)
    iopsInit = len(iops.axes)
    bw = plot.figure(figsize=(20,15))
    bw.suptitle("Bandwidth MB/s", fontsize=20)
    bwInit = len(bw.axes)
    latency = plot.figure(figsize=(20,15))
    latency.suptitle("Latency, MicroSec.", fontsize=20)
    latencyInit = len(latency.axes)
    xCpu = plot.figure(figsize=(20,15))
    xCpu.suptitle("X-ENV Utilization", fontsize=20)
    xCpuInit = len(xCpu.axes)
    for name in xmsData.dtype.names:
        if re.search('iops', name):
            drawPlots(xmsData,iops,name,"IOPs",iopsInit+1)
        if re.search('bandwidth', name):
            drawPlots(xmsData,bw,name,"Bandwidth, MB/s", bwInit+1)
        if re.search('latency', name):
            drawPlots(xmsData,latency,name,"Latency, MicroSec", latencyInit+1)
    for name in xenvData.dtype.names:
        drawPlots(xenvData,xCpu,name,"% CPU Utilization", xCpuInit+1)
    pdfDoc = PdfPages('XtremPerfcharts.pdf')
    pdfDoc.savefig(iops)
    pdfDoc.savefig(bw)
    pdfDoc.savefig(latency)
    pdfDoc.savefig(xCpu)
    pdfDoc.close()
    plot.close(iops)
    plot.close(bw)
    plot.close(latency)
    plot.close(xCpu)
    # plot.show()

def drawVolPerfCharts(vol):
    volData = np.genfromtxt('%s.csv' % (vol), dtype=float, delimiter=',', names=True)
    plot.ioff()
    iops = plot.figure(figsize=(20,15))
    iops.suptitle("IOPs", fontsize=20)
    iopsInit = len(iops.axes)
    bw = plot.figure(figsize=(20,15))
    bw.suptitle("Bandwidth MB/s", fontsize=20)
    bwInit = len(bw.axes)
    latency = plot.figure(figsize=(20,15))
    latency.suptitle("Latency, MicroSec.", fontsize=20)
    latencyInit = len(latency.axes)
    for name in volData.dtype.names:
        if re.search('iops', name):
            drawPlots(volData,iops,name,"IOPs",iopsInit+1)
        if re.search('bandwidth', name):
            drawPlots(volData,bw,name,"Bandwidth, MB/s", bwInit+1)
        if re.search('latency', name):
            drawPlots(volData,latency,name,"Latency, MicroSec", latencyInit+1)
    pdfDoc = PdfPages('%s.pdf' %(vol))
    pdfDoc.savefig(iops)
    pdfDoc.savefig(bw)
    pdfDoc.savefig(latency)
    pdfDoc.close()
    plot.close(iops)
    plot.close(bw)
    plot.close(latency)

def drawEsxCharts(hostname,storageHba):
    pdfDoc = PdfPages('host_%s.pdf'%(hostname))
    data = np.genfromtxt('%s.csv' %(hostname), dtype=float, delimiter=',', names=True)
    # print data.dtype.names
    cpu = plot.figure(figsize=(20,15))
    cpu.suptitle("% CPU-Utilization", fontsize=20)
    cpuInit = len(cpu.axes)
    memory = plot.figure(figsize=(20,15))
    memory.suptitle("% Memory Usage", fontsize=20)
    memoryInit = len(memory.axes)
    for name in data.dtype.names:
        if re.match('CPU_Utilization', name):
            plotName = '% CPU Util'
            drawPlots(data,cpu,name,"% CPU Util",cpuInit+1)
        if re.match('Memory_Usage', name):
            plotName = '% Usage'
            drawPlots(data,memory,name,"% Memory Usage", memoryInit+1)
    for hba in storageHba:
        hba_iops = plot.figure(figsize=(20,15))
        hba_iops.suptitle("%s IOPs"%(hba), fontsize=20)
        hbaIopsInit = len(hba_iops.axes)
        hba_bw = plot.figure(figsize=(20,15))
        hba_bw.suptitle("%s Bandwidth"%(hba), fontsize=20)
        hbaBwInit = len(hba_bw.axes)
        hba_latency = plot.figure(figsize=(20,15))
        hba_latency.suptitle("%s Latency"%(hba), fontsize=20)
        hbaLatencyInit = len(hba_latency.axes)
        for name in data.dtype.names:
            if re.search('Storage_adapter%s'%(hba), name) and re.search('requests_per_second', name):
                plotName = '%s IOPs' %(hba)
                drawPlots(data,hba_iops,name,"IOPs",hbaIopsInit+1)
            if re.search('Storage_adapter%s'%(hba), name) and re.search(r'_rate_average', name):
                plotName = 'Bandwidth Utilization'
                drawPlots(data,hba_bw,name,"Bandwidth Utilization", hbaBwInit+1)
            if re.search('Storage_adapter%s'%(hba), name) and re.search(r'_latency_average', name):
                plotName = 'Latency'
                drawPlots(data,hba_latency,name,"Latency (msec)", hbaLatencyInit+1)
        pdfDoc.savefig(hba_latency)
        pdfDoc.savefig(hba_iops)
        pdfDoc.savefig(hba_bw)
    pdfDoc.savefig(cpu)
    pdfDoc.savefig(memory)
    pdfDoc.close()
    plot.close(hba_iops)
    plot.close(hba_bw)
    plot.close(hba_latency)
    plot.close(cpu)
    plot.close(memory)
    # plot.show()

def main():
    drawXtremIOCharts()
    # data = np.genfromtxt('xtremPerfStats.csv', dtype=float, delimiter=',', names=True)
    # print data.dtype.names
    # iops = plot.figure()
    # iopsInit = len(iops.axes)
    # bw = plot.figure()
    # bwInit = len(bw.axes)
    # latency = plot.figure()
    # latencyInit = len(latency.axes)
    # xCpu = plot.figure()
    # xCpuInit = len(xCpu.axes)
    # for name in data.dtype.names:
    #     if re.search('iops', name):
    #         drawPlots(data,iops,name,"IOPs",iopsInit+1)
    #     if re.search('bandwidth', name):
    #        drawPlots(data,bw,name,"Bandwidth, MB/s", bwInit+1)
    #     if re.search('latency', name):
    #        drawPlots(data,latency,name,"Latency, MicroSec", latencyInit+1)
    #     if re.search('SC', name):
    #         drawPlots(data,xCpu,name,"% CPU Utilization", xCpuInit+1)
    # plot.show()


if __name__ == '__main__':
    main()