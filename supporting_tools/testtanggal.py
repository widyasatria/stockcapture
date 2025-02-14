from datetime import datetime
import time

start_time = datetime.now()
tgls= "2023-09-01T00:00:00+0000"
t1 = tgls.split("T")
t2=t1[0].split("-")
tanggal = datetime(int(t2[0]),int(t2[1]),int(t2[2]))
                   
print( "sasda ", tanggal)
time.sleep(3)
end_time = datetime.now()
print('Duration: {}'.format(end_time - start_time))