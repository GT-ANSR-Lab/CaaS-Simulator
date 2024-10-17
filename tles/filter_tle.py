def myFunc(e):
  return e['index']

all_tles = []
with open('./tmp/all_starlink_53.txt') as f:
    line1 = f.readline()
    while line1:
        line2 = f.readline()
        line3 = f.readline()
        x = {'tle': line1+line2+line3, 'index': float(line3.split()[3])}
        all_tles.append(x)
        line1 = f.readline()
all_tles.sort(key=myFunc)
#print(all_tles)
#list_of_orbit_param = [4, 12, 24, 36, 48, 56, 76, 94, 112, 125, 137, 157, 184, 194, 211, 224, 239, 256, 284, 320, 330]
list_of_orbit_param = [12, 56, 94, 157, 194, 284, 330]
#list_of_orbit_param = [13, 30, 51, 100, 178]
#list_of_orbit_param = [17, 39, 289, 312]
for l in all_tles:
  #print(int(round(l['index'])))
  if(int(round(l['index'])) in list_of_orbit_param):
    #print(int(round(l['index'])))
    print(l['tle'], end='')