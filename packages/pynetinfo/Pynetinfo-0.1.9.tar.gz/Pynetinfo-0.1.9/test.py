import netinfo
for dev in netinfo.list_active_devs():
	print "*********************************"
	print dev
	print "mac: "+netinfo.get_hwaddr(dev)
	print "ip: "+netinfo.get_ip(dev)
	print "netmask: "+netinfo.get_netmask(dev)
	print "broadcast: "+netinfo.get_broadcast(dev)
print "######################################"
for route in netinfo.get_routes():
    print route['dest']+"/"+route['netmask']+" -> "+route['gateway']


#netinfo.del_route("", "192.168.0.0", "164.11.222.253", "255.255.255.0");
