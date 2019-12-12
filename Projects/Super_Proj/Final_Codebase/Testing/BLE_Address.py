import pexpect

results = open("scan_results.txt", 'w+')
child = pexpect.spawn("bluetoothctl")
child.send("scan on\n")
bdaddrs = []
count = 0
stored_address = "b'F4:C2:48:50:82:1C'"

try:
    while (count < 300):
        child.expect("Device (([0-9A-Fa-f]{2}:){5}([0-9A-Fa-f]{2}))")
        bdaddr = child.match.group(1)
        if bdaddr not in bdaddrs:
            #print(bdaddr)
            bdaddrs.append(bdaddr)
            results.write(str(bdaddr))
            results.write('\n')
            print(str(bdaddr))
            if(str(bdaddr) == stored_address):
                print("Successful\n")
                break
        count+=1
    results.close()
    
    if(count == 300):
        print("Failure\n")
           
#    results = open("scan_results.txt", 'r') 
#    addr_stored = results.readlines()
#    for i in addr_stored:
#        print(i)
#        if(i == stored_address):
#            print("Successful\n")
#            break
#    results.close()
    
except KeyboardInterrupt:
    child.close()
    results.close()