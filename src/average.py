import os
import csv
import sys

avg_acc = {}
output_files_dir = sys.argv[1]

# Precaution
if output_files_dir[-1] != "/":
    output_files_dir += "/"

ctr  = 0
for filename in os.listdir(output_files_dir):
    if filename[-3:] == "csv":
        ctr += 1
        with open(output_files_dir + filename, 'r') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            first_line = True
            for row in csv_reader:
                if first_line:
                    first_line = False
                else:
                    if row[0] not in avg_acc:
                        avg_acc[row[0]] = float(row[2])
                    else:
                        avg_acc[row[0]] += float(row[2])

for k in avg_acc:
    print(k, "\t\t" , avg_acc[k] / ctr)
