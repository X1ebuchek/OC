# memory
import subprocess
import time

import matplotlib.pyplot as plt

MEASURE_TIME = 30
HOGS = 9
METH = "zlib-mem-level"
COMMAND = f"stress-ng --zlib 4 --{METH} {HOGS} --timeout {MEASURE_TIME + 5}s"

cpus = {}
mems = {}
points = {}

proc = subprocess.Popen([COMMAND], shell=True, stdin=None, stdout=None, stderr=None, close_fds=True)
time.sleep(0.5)

pids = subprocess.check_output(["pgrep", "stress-ng"]).decode("utf-8").split("\n")[1:-1]
print(f"Runners {len(pids)}: {pids}")

pids_line = ','.join(pids)

for i in pids:
    cpus[i] = []
    mems[i] = []
    points[i] = []

PID_COMMAND = "top -b -p %s -n 1"

start_time = time.time()

while time.time() - start_time < MEASURE_TIME:

    output = subprocess.check_output((PID_COMMAND % pids_line).split())

    res = output.decode("utf-8").splitlines()[7:]

    for pid, line in zip(pids, res):

        norm_line = [i.strip() for i in line.split() if not i.isspace() and i]

        param_cpu = norm_line[8]
        param_mem = norm_line[9]

        cpus[pid].append(float(param_cpu.replace(',', '.')))
        mems[pid].append(float(param_mem.replace(',', '.')))
        points[pid].append(time.time() - start_time)

fig, ax = plt.subplots(2)
for i in pids:
    ax[0].plot(points[i], cpus[i], label=i)
    ax[1].plot(points[i], mems[i], label=i)

ax[0].set_ylabel("%CPU")
ax[0].set_xlabel("Time(сек)")

ax[1].set_ylabel("%MEM")
ax[1].set_xlabel("Time(сек)")

plt.subplots_adjust(hspace=0.5)
plt.savefig(f"mem_{METH}_{HOGS}_{MEASURE_TIME}.png")