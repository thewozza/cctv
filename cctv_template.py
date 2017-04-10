import csv
import sys

print "Syntax is ", sys.argv[0], "[room] [rack]"

# this is the csv file that contains Dan's port assignments
with open('cctv.csv', 'rU') as f1:
	reader = csv.reader(f1)
	header = next(reader)
	ports = list(list(rec) for rec in csv.reader(f1, delimiter=',')) #reads csv into a list of lists

# this is the VLAN to switch stack reference file
# this file should never change
vlan_data = dict()
with open("cctv_vlans.csv", "rb") as vlan_file:
    vlans = csv.DictReader(vlan_file)
    for row in vlans:
		vlan_data[(row["Room"],row["Rack"])] = {"VLAN" : row["VLAN"]}

# this section prints the instructions if no parameters are given
# it prints the rooms and racks that Dan has assigned ports for
if len(sys.argv) == 1:
	print "Rooms and Racks available for configuration"
	for port_row in ports:
		if port_row[9] == "" :
			continue
		else:
			room = port_row[2].split('-')[1]
			rack = port_row[9].split('-')[0].split('S')[0]
			print "Room:", room, "Rack:", rack
	sys.exit()				# this drops right out of the script
# if we get to this point it means that someone added a CLI parameter
elif len(sys.argv) == 2:	# only one parameter given
							# this is assumed to be the room
	req_room = sys.argv[1]
else:						# both parameters given
							# assumed to be in the order [room] [rack]
	req_room = sys.argv[1]
	req_rack = sys.argv[2]

# this section rolls through all the available lines in Dan's port
# assignment CSV file
# it skips unconfigured lines
# it skips those that aren't specified by the command line parameters
for port_row in ports:
	if port_row[9] == "" :	# skip if Dan hasn't filled this in
		continue
	else:
		# test if we're on a line that matches the room we're working with
		room = port_row[2].split('-')[1]
		if room != req_room: continue
		
		# test if we're on a line that matches the rack we're working with
		rack = port_row[9].split('-')[0].split('S')[0]
		if 'req_rack' in locals():
			if rack != req_rack: continue
		
		# now that we're on a good line, we complete the rest of the 
		# variables
		camera = port_row[0]
		port = port_row[9].split('-')[1].split('P')[1].lstrip("0")
		switch = port_row[9].split('-')[0].split('S')[1].strip(" ")
		
		# and finally print the configuration snippet
		print "# TAC-" + str(room) + "-" + str(rack) + "SW" + str(switch)
		print ""
		print "interface GigabitEthernet" + str(switch) + "/0/" + str(port)
		print "  description TAC-" + str(room) + "-" + str(rack) + "SW" + str(switch) + "-Security Access Control / CCTV / Intercom Camera " + str(camera)
		print "  switchport access vlan", vlan_data[(room,rack)]["VLAN"]
		print """  switchport mode access
  switchport port-security maximum 3
  switchport port-security violation restrict
  switchport port-security aging time 1
  switchport port-security aging type inactivity
  switchport port-security
  ip arp inspection limit rate 50 burst interval 3
  no snmp trap link-status
  spanning-tree portfast
  spanning-tree bpduguard enable
  """