import subprocess
import time

import matplotlib.pyplot as plt

MEASURE_TIME = 40
CORES = 8
COMMAND = f"stress-ng --cpu-method div32 --cpu {CORES} --timeout {MEASURE_TIME + 5}s --metrics"

results = {}
points = {}

proc = subprocess.Popen([COMMAND], shell=True, stdin=None, stdout=None, stderr=None, close_fds=True)

time.sleep(2)

pids = subprocess.check_output(["pgrep", "stress-ng"]).decode("utf-8").split("\n")[1:-1]
print(f"Runners: {pids}")

for i in pids:
    results[i] = []
    points[i] = []


TOP_COMMAND = "top -b -p %s -n 1"
GREP_COMMAND = "grep %s"

start_time = time.time()

while time.time() - start_time < MEASURE_TIME:

    for proc in results:

        ps = subprocess.Popen((TOP_COMMAND % proc).split(), stdout=subprocess.PIPE)
        output = subprocess.check_output((GREP_COMMAND % proc).split(), stdin=ps.stdout)
        ps.wait()

        res = output.decode("utf-8").split(" ")
        res = [i.strip() for i in res if not i.isspace() and i]

        param = res[8]

        results[proc].append(float(param.replace(',', '.')))
        points[proc].append(time.time() - start_time)


fig, ax = plt.subplots()
for i in results:
    ax.plot(points[i], results[i], label=i)
ax.set_ylabel("CPU%")
ax.set_xlabel("Time(сек)")
ax.set_ylim([0, 105])
ax.legend()
plt.savefig(f"cpu_big_{CORES}.png")