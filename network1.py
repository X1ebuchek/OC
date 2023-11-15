# network
import subprocess
import time

import matplotlib.pyplot as plt

MEASURE_TIME = 30
HOGS = 1
METH = "netlink-proc"
COMMAND = f"sudo stress-ng --{METH} {HOGS} --timeout {MEASURE_TIME + 5}s"

received = []
sent = []
points = []

proc = subprocess.Popen([COMMAND], shell=True, stdin=None, stdout=None, stderr=None, close_fds=True)
time.sleep(1)

pids = subprocess.check_output(["pgrep", "stress-ng"]).decode("utf-8").split("\n")[1:-1]
print(f"Runners {len(pids)}: {pids}")

IP_COMMAND = "ip -s link show wlp0s20f3"

output = subprocess.check_output(IP_COMMAND.split()).decode("utf-8").splitlines()
norm_start_rx = [i.strip() for i in output[3].split() if not i.isspace() and i]
start_rx = int(norm_start_rx[0])

norm_start_tx = [i.strip() for i in output[5].split() if not i.isspace() and i]
start_tx = int(norm_start_tx[0])

start_time = time.time()

while time.time() - start_time < MEASURE_TIME:

    output = subprocess.check_output(IP_COMMAND.split()).decode("utf-8").splitlines()
    norm_start_rx = [i.strip() for i in output[3].split() if not i.isspace() and i]

    rx = int(norm_start_rx[0])

    norm_start_tx = [i.strip() for i in output[5].split() if not i.isspace() and i]
    tx = int(norm_start_tx[0])

    received.append(rx - start_rx)
    sent.append(tx - start_tx)
    points.append(time.time() - start_time)

    start_tx, start_rx = tx, rx

    time.sleep(0.99)


fig, ax = plt.subplots(2)

ax[0].plot(points, received, label="Received (bytes)")
ax[1].plot(points, sent, label="Sent (bytes)")

ax[0].set_ylabel("Bytes")
ax[0].set_xlabel("Time(сек)")

ax[1].set_ylabel("Bytes")
ax[1].set_xlabel("Time(сек)")

plt.subplots_adjust(hspace=0.5)
plt.savefig(f"net_{METH}_{HOGS}_{MEASURE_TIME}.png")