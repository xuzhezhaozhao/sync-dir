import xlwt
import commands
import os

data_dir = "/home/admin/ceph-test-data"
pangu_result_file = os.path.join(data_dir, "pangu_result.txt")
blocks = [2**x for x in range(2,13)]
mods=["write", "seq", "rand"]
threads = [2**x for x in range(0,11)]
runtime = 100




def generate_xls(thread, runtime = 60, row = 0, col = 0, singlenode = 0):
    heads = [ 
                "Block size (KB)", 
                "Throughput-wirte(MB/s)",  "Latency-write(ms)", "IOPS-write",
                "Bandwidth-seqread(MB/s)",  "Latency-seqread(ms)", "IOPS-seqread",
                "Bandwidth-randread(MB/s)",  "Latency-randread(ms)", "IOPS-randread",
            ]
    # add heads
    begin_col = col
    sheet.col(col).width = 256*20
    sheet.write(row, col, "concurrent num")
    col += 1
    sheet.write(row, col, thread)
    row += 1
    col = begin_col

    for i in range(col, col+len(heads)):
        # set column width
        sheet.col(i).width = 256*20
        sheet.write(row, i, heads[i])

    # fill data
    row += 1
    for b in blocks:
        sheet.write(row, col, b)
        col += 1
        for mod in mods:
            sum_bandwidth = 0
            sum_latency = 0
            cnt = 0
            for i in range(4, 12):
                if singlenode and i > 4:
                    break

                filename = "ceph_bench" + str(i) +  "_" + mod + "_" + "thread" + str(thread) + "_"  + "block" + str(b) + \
                            "_" + "runtime" + str(runtime)
                if singlenode:
                    filename += "_singlenode"
                filename += ".out"

                filename = os.path.join(data_dir, filename)
                
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
            avg_latency   = sum_latency*1.0 / cnt*1000
            avg_iops      = avg_bandwidth*1024*1.0 / b

            # write data to corresponding cell
            sheet.write(row, col, avg_bandwidth)
            col += 1
            sheet.write(row, col, avg_latency)
            col += 1
            sheet.write(row, col, avg_iops)
            col += 1

        row += 1
        col = begin_col

def generate_xls_for_pangu(thread, runtime = 60, row = 0, col = 0, singlenode = 0):
    heads = [ 
                "cocurrents num",
#"Block size (KB)", 
                "Throughput-wirte(MB/s)",  "Latency-write(ms)", "IOPS-write",
                "Bandwidth-seqread(MB/s)",  "Latency-seqread(ms)", "IOPS-seqread",
                "Bandwidth-randread(MB/s)",  "Latency-randread(ms)", "IOPS-randread",
            ]
    begin_col = col

    for i in range(col, col+len(heads)):
        # set column width
        sheet.col(i).width = 256*20
        sheet.write(row, i, heads[i])

    linenum = 0
    for line in open(pangu_result_file):
        c = linenum % 6
        if c == 0:
            # begin a new record
            col = begin_col
            row += 2
        elif c == 1:
            # latency
            latency = line.split()[2]
            sheet.write(row, col, latency)
            col += 1
        elif c == 2:
            pass
        elif c == 3:
            # thoughput
            thoughput = line.split()[2]
            sheet.write(row, col, thoughput)
            col += 1
        elif c == 4:
            # qps
            qps = line.split()[2]
            sheet.write(row, col, qps)
        else:
            pass

        linenum += 1



if __name__ == '__main__':
    workbook = xlwt.Workbook()
    sheet = workbook.add_sheet('ceph-results')
    row = 0
    sheet.write(row, 0, 'multi node: node4~11')
    row += 1
    for thread in threads: 
        generate_xls(thread, runtime, row, 0)
        row += 18

    sheet.write(row, 0, 'singlenode: node4')
    row += 1
    for thread in threads:
        generate_xls(thread, runtime, row, 0, 1)
        row += 18

    sheet = workbook.add_sheet('pangu-results')
    generate_xls_for_pangu(thread, runtime, 0, 0)

    workbook.save('/home/admin/sync-dir/ceph-results.xls')
