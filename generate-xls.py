import xlwt
import commands

workbook = xlwt.Workbook()
sheet = workbook.add_sheet('ceph-results')

# add heads
heads = [ 
            "Block size (KB)", 
            "Bandwidth (wirte)",  "Latency (write)", "IOPS (write)",
            "Bandwidth (seq read)",  "Latency (seq read)", "IOPS (seq read)",
            "Bandwidth (rand read)",  "Latency (rand read)", "IOPS (rand read)",
        ]
for i in range(0, len(heads)):
    # set column width
    sheet.col(i).width = 256*20
    sheet.write(0, i, heads[i])

# fill data
thread=128
runtime=60
mods=["write", "seq", "rand"]

row = 1
col = 0
blocks = [2**x for x in range(2,13)]
for b in blocks:
    sheet.write(row, col, b)
    col += 1
    for mod in mods:
        sum_bandwidth = 0
        sum_latency = 0
        cnt = 0
        for i in range(4, 12):
            filename = "ceph_bench" + str(i) +  "_" + mod + "_" + "thread" + str(thread) + "_"  + "block" + str(b) + \
                        "_" + "runtime" + str(runtime) + ".out"
            
            cmd_bandwidth = "grep 'Bandwidth (MB/sec):' " + filename + " | awk '{ printf $3}'"
            cmd_latency   = "grep 'Average Latency:' "    + filename + " | awk '{ printf $3}'"

            print "excuting " + cmd_bandwidth + "..."
            print "excuting " + cmd_latency + "..."

            status1, bandwidth = commands.getstatusoutput(cmd_bandwidth);
            status2, latency   = commands.getstatusoutput(cmd_latency);
            if status1 != 0 or status2 != 0:
                print "Error!!!"
                print bandwidth
                print latency 
                sys.exit(-1)

            print "cmds excuted ok"

            cnt += 1
            sum_bandwidth += float(bandwidth)
            sum_latency   += float(latency)

        avg_bandwidth = sum_bandwidth*1.0 / cnt
        avg_latency   = sum_latency*1.0 / cnt
        avg_iops      = avg_bandwidth*1024*1.0 / b

        # write data to corresponding cell
        sheet.write(row, col, avg_bandwidth)
        col += 1
        sheet.write(row, col, avg_latency)
        col += 1
        sheet.write(row, col, avg_iops)
        col += 1

    row += 1
    col = 0


workbook.save('/home/admin/sync-dir/ceph-results.xls')
