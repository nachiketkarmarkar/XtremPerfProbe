# XtremPerfProbe
XtremPerfProbe is a python based tool helps root causing performance bottlenects in a virtualized environment (VMware vSphere) with EMC XtremIO has SAN storage

## Description
XtremPerfProbe has the ability to collect performance stats on entire cluster, on a list of select ESX hosts and on a list of select XtremIO volumes. For collecting stats at a cluster scope and per volume scope it uses XtremIO REST API query and directly reads the stats from XMS. For collecting stats for ESX hosts, it queries vCenter database and collects the same stats as seen in VMware vCentner Server UI's performance tab. Following stats are recorded for:

#### XtremIO cluster:
1. Read IO Bandwidth
2. Write IO Bandwidth
3. Total IO Bandwidth
4. Read IOPs
5. Write IOPs
6. Total IOPs
7. Read latency
8. Write latency
9. % X-ENV Utilization for all SCs and all X-bricks in the cluster

#### Xtrem IO Volume:
1. Read IO Bandwidth
2. Write IO Bandwidth
3. Total IO Bandwidth
4. Read IOPs
5. Write IOPs
6. Total IOPs
7. Read latency
8. Write latency

#### ESX hosts:
1. % CPU utilization
2. Memory Utilization
3. Network bandwidth consumption
4. For all HBAs:
	a. Read IO Bandwidth
 	b. Write IO Bandwidth
 	c. Total IO Bandwidth
 	d. Read IOPs
	e. Write IOPs
	f. Total IOPs
	g. Read latency
	h. Write latency
4. For all vSphere SCSI Disk objects:
	a. Read IO Bandwidth
 	b. Write IO Bandwidth
 	c. Total IO Bandwidth
 	d. Read IOPs
	e. Write IOPs
	f. Total IOPs
	g. Read latency
	h. Write latency

#### Results:
All performance statistics are recorded in .csv files. Users can open these files in Microsoft excel refer to them or save it for the records. There is one single .csv file for XtremIO cluster stats, one .csv file per ESX host and one .csv file per XtremIO volume.

Similar to .csv files, it also generates .pdf files that contain charts for performance stats collected. There is one .pdf file for XtremIO cluster stats, one .pdf file per ESX host and one .pdf file per XtremIO volume. Looking at charts, we can quickly identify outliers and bottlenects.

## Installation
- Make sure you are running Python 2.7.10 and pip is installed
- Using pip, download and install pyVmomi
- Using pip, download and install numpy
- Using pip, download and install matplotlib
- Download the python files in your working directory
- In the same working directory download all python modules located in Github's PyXtrem repository below:
  - https://github.com/nachiketkarmarkar/PyXtrem

## Usage Instructions
In order to learn about different options to pass to the script, run:

python collectPerfStats.py -h

This will give the following output

Usage: collectPerfStats.py -<option>  <parameter>
    
                      -i     <XMS Server IP>                        or            --xmsip     <XMS Server IP>
                      -u     <XMS username>                         or            --xmsuser   <XMS username>*
                      -p     <XMS password>                         or            --xmspwd    <XMS password>*
                      -v     <vCenter Server IP>                     or            --vcip      <vCenter Server IP>
                      -l     <vCenter server username>               or            --vcuser    <vCenter server username>
                      -c     <vCenter Server password>               or            --vcpwd     <vCenter Server password>
                      -d     <duration>*                             or            --duration  <duration>
                      -e     <comma separated FQDN of ESX hosts>     or            --hostnames <comma separated FQDN of ESX hosts>
                      -x     <comma separated XtremIO volume names   or            --volumes   <comma separated XtremIO volume names
                      -s     <sampling frequency in seconds>*        or            --sampling  <sampling frequency in seconds>
    
'*' Indicates essential parameter and has to be given. Make sure sampling frequency is more than 5 seconds

Among all the arguments, 'duration' and 'sampling frequency' is a mandatory. Also, users need to give either one of the following two sets of arguments:

Set #1: -i, -u, -p (XMS Server IP, XMS username, XMS Password)
Set #2: -v, -l, -c (VC IP Address, VC username, VC password)

This enables users to collect just the XtremIO statistics or only the vSphere statistics or both.

Users have an option to provide a comma separated list of XtremIO volumes where they want to collect performance statistics. However, collecting performance statistics per volume is optional.

## Future
- Currently, stats collection on ESX hosts is limited to FC HBAs. ISCSI support may be added at a later date
- Virtualized environments using VMware vSphere as virtualization platform are supported. Hyver-V and XenServer may be added at a later date

## Contribution
Create a fork of the project into your own reposity. Make all your necessary changes and create a pull request with a description on what was added or removed and details explaining the changes in lines of code. If approved, project owners will merge it.

Licensing
---------
XtremPerfProbe is freely distributed under the [MIT License](http://emccode.github.io/sampledocs/LICENSE "LICENSE"). See LICENSE for details.

Support
-------
Please file bugs and issues on the Github issues page for this project. This is to help keep track and document everything related to this repo. For general discussions and further support you can join the [EMC {code} Community slack channel](http://community.emccode.com/). Lastly, for questions asked on [Stackoverflow.com](https://stackoverflow.com) please tag them with **EMC**. The code and documentation are released with no warranties or SLAs and are intended to be supported through a community driven process.
