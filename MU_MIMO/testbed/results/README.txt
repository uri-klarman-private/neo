testbed components:
-------------------

In order to achieve a working testbed without using promiscuous mode in the NICs or tcpdump at the AP,
we will use the following components:

# 1 MU-MIMO AP
# 15 clients (C_1-15) connected to the AP using MU-MIMO NIC
# 1 broadcast client (BC), who will continuously broadcast the 15 clients
# 1 traffic generating server (S), which will send packets with varying sizes to all the 15 clients
# 1 monitoring client (M), which will track the sounding procedure of everyone.


testbed flow:
-------------

1. S connects with Ethernet to AP, waiting to receive 16 packets
2. 15 clients connect to wifi, each send a single packet to S, and start accepting traffic.
3. 