import sys
import re
import json
from typing import final
import xmltodict
from pprint import pprint
import xmind

xml2json =  {}

def usage():
	print("Usage:")
	print("python3 mind_n_map.py [nmap_output.xml]")

def extract_from_json(o):
	final_dict={}
	services = []
	
	hosts = o["nmaprun"]["host"]
	try:
		hosts['address']
		hosts = [hosts]
	except:
		pass
	try:
		hosts['adress']
		hosts=[hosts]
	except:
		pass
	'''extract current host'''
	for host in hosts:
		if(type(host['address']) == list):
			current_host = (host['address'][0]['@addr'])
		else:
			current_host = (host['address']['@addr'])

		'''extract services'''
		ports = host['ports']['port']
		if type(ports)==list:
			for port in ports:
				services.append({
					"proto": port['@protocol'],
					"port": port['@portid'],
					"state": port['state']['@state'],
					"service": port['service']['@name'],
				})
		else:
			services.append({
					"proto": ports['@protocol'],
					"port": ports['@portid'],
					"state": ports['state']['@state'],
					"service": ports['service']['@name'],
			})
		final_dict.update({current_host:services})
		services=[]
	return final_dict




'''main'''
try:
	nmap_file = sys.argv[1]
except:
	usage()
	sys.exit()

nmap_output = open(nmap_file, "r").read() # get content from input file
xml2json = json.loads(json.dumps(xmltodict.parse(nmap_output))) # parse xml to get a json
nmap = extract_from_json(xml2json) # extract what we need from json

IPs = []
xmind_file=nmap_file.split(".")[0]+".xmind"
w = xmind.load(xmind_file)# load , If it doesn't exist , Create a new file
page=w.getPrimarySheet() # Get the first page
page.setTitle(xmind_file) # Name the first page

root=page.getRootTopic() # Create a root node
root.setTitle(nmap_file.split(".")[0]) # Name the root node with the file name 


'''add hosts to the xmind file'''
count=0
for host in nmap:
	#print(host)
	IPs.append(root.addSubTopic())
	IPs[count].setTitle(str(host))
	count+=1


'''add ports and banners to the xmind file'''
port=[]
IP_COUNT=0

'''iterate the hosts'''
for host in nmap:
	port=[]
	banner=[]
	count=0

	'''iterate the services and add them to its host'''
	for servico in nmap[host]:
		print("A adicionar o porto {0} ao IP {1}".format(servico['port'],host))
		
		'''add port'''
		port.append(IPs[IP_COUNT].addSubTopic())
		port[count].setTitle(str(servico['port']+"/"+servico['proto']))
		
		'''add service name'''
		banner.append(port[count].addSubTopic())
		banner[count].setTitle(str(servico['service']))
		count+=1
	IP_COUNT+=1
	print("\n")


xmind.save(w,xmind_file) ## Save the file 
