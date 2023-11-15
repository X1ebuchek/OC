import subprocess
import time

import matplotlib.pyplot as plt

MEASURE_TIME = 60
HOGS = 2
METH = "io-uring"
COMMAND = f"stress-ng --{METH} {HOGS} --timeout {MEASURE_TIME + 5}s"

reads = {}
writes = {}
points = {}

proc = subprocess.Popen([COMMAND], shell=True, stdin=None, stdout=None, stderr=None, close_fds=True)
time.sleep(0.5)

pids = subprocess.check_output(["pgrep", "stress-ng"]).decode("utf-8").split("\n")[1:-1]
print(f"Runners {len(pids)}: {pids}")

pids_line = ','.join(pids)

for i in pids:
    reads[i] = []
    writes[i] = []
    points[i] = []

PID_COMMAND = "pidstat -d -p %s"

start_time = time.time()

while time.time() - start_time < MEASURE_TIME:

    output = subprocess.check_output((PID_COMMAND % pids_line).split())

    res = output.decode("utf-8").splitlines()[3:]

    for pid, line in zip(pids, res):

        norm_line = [i.strip() for i in line.split() if not i.isspace() and i]

        param_read = norm_line[3]
        param_write = norm_line[4]

        reads[pid].append(float(param_read.replace(',', '.')))
        writes[pid].append(float(param_write.replace(',', '.')))
        points[pid].append(time.time() - start_time)

fig, ax = plt.subplots(2)
for i in pids:
    ax[0].plot(points[i], reads[i], label=i)
    ax[1].plot(points[i], writes[i], label=i)

ax[0].set_ylabel("kB_rd/s")
ax[0].set_xlabel("Time(сек)")

ax[1].set_ylabel("kB_wr/s")
ax[1].set_xlabel("Time(сек)")

plt.subplots_adjust(hspace=0.5)
plt.savefig(f"io_{METH}_{HOGS}_{MEASURE_TIME}.png")