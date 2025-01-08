from prometheus_client import start_http_server, Gauge
import time
import subprocess

# Define Prometheus metrics
# HW Counters for ROCEv2
np_ecn_marked_roce_packets = Gauge('rdma_np_ecn_marked_roce_packets', 'Number of ROCEv2 packets marked for congestion', ['hostname', 'interface'])
out_of_sequence = Gauge('rdma_out_of_sequence', 'Number of out of sequence packets received.', ['hostname', 'interface'])
packet_seq_err = Gauge('rdma_packet_seq_err', 'Number of received NAK sequence error packets', ['hostname', 'interface'])
local_ack_timeout_err = Gauge('rdma_local_ack_timeout_err', 'Number of times QPs ack timer expired', ['hostname', 'interface'])
roce_adp_retrans = Gauge('rdma_roce_adp_retrans', 'Number of adaptive retransmissions for RoCE traffic', ['hostname', 'interface'])
np_cnp_sent = Gauge('rdma_np_cnp_sent', 'Number of CNP packets sent', ['hostname', 'interface'])
rp_cnp_handled = Gauge('rdma_rp_cnp_handled', 'Number of CNP packets handled to throttle', ['hostname', 'interface'])
rp_cnp_ignored = Gauge('rdma_rp_cnp_ignored', 'Number of CNP packets received and ignored', ['hostname', 'interface'])
rx_icrc_encapsulated = Gauge('rdma_rx_icrc_encapsulated', 'Number of RoCE packets with ICRC (Invertible Cyclic Redundancy Check) errors', ['hostname', 'interface'])
roce_slow_restart = Gauge('rdma_roce_slow_restart', 'Number of times RoCE slow restart was used', ['hostname', 'interface'])
# Port Counters for Infiniband
ib_link_state = Gauge('ib_link_state', 'Port State', ['hostname', 'interface'])
ib_link_phys_state = Gauge('ib_link_phys_state', 'Port Physical State', ['hostname', 'interface'])
ib_symbol_error = Gauge('ib_symbol_error', 'Total number of minor link errors detected on one or more physical lanes', ['hostname', 'interface'])
ib_port_rcv_errors = Gauge('ib_port_rcv_errors', 'Total number of packets containing an error that were received on the port', ['hostname', 'interface'])
ib_port_rcv_remote_phsyical_errors = Gauge('ib_port_rcv_remote_phsyical_errors', 'Total number of packets marked with the EBP delimiter received on the port', ['hostname', 'interface'])
ib_port_rcv_switch_relay_errors = Gauge('ib_port_rcv_switch_relay_errors', 'Total number of packets received on the port that were discarded because they could not be forwarded by the switch relay', ['hostname', 'interface'])
ib_link_error_recovery = Gauge('ib_link_error_recovery', 'Total number of times the Port Training state machine has successfully completed the link error recovery process', ['hostname', 'interface'])
ib_port_xmit_constraint_errors =  Gauge('ib_port_xmit_constraint_errors', 'Total number of packets not transmitted from the switch physical port due to outbound raw filtering or failing outbound partition or IP version check', ['hostname', 'interface'])
ib_port_rcv_contraint_errors = Gauge('ib_port_rcv_contraint_errors', 'Total number of packets received on the switch physical port that are discarded due to inbound raw filtering or failing inbound partition or IP version check.', ['hostname', 'interface'])
ib_local_link_integrity_errors = Gauge('ib_local_link_integrity_errors', 'The number of times that the count of local physical errors exceeded the threshold specified by LocalPhyErrors', ['hostname', 'interface'])
ib_excessive_buffer_overrun_errors = Gauge('ib_excessive_buffer_overrun_errors', 'This counter, indicates an input buffer overrun. It indicates possible misconfiguration of a port, either by the Subnet Manager (SM) or by user intervention. It can also indicate hardware issues or extremely poor link signal integrity', ['hostname', 'interface'])
ib_port_xmit_data = Gauge('ib_port_xmit_data', 'Total number of data octets, divided by 4 (lanes), transmitted on all VLs', ['hostname', 'interface'])
ib_port_rcv_data = Gauge('ib_port_rcv_data', 'Total number of data octets, divided by 4 (lanes), received on all VLs', ['hostname', 'interface'])
ib_port_xmit_packets = Gauge('ib_port_xmit_packets', 'Total number of packets transmitted on all VLs from this port. This may include packets with errors', ['hostname', 'interface'])
ib_port_rcv_packets = Gauge('ib_port_rcv_packets', 'Total number of packets received on all VLs from this port. This may include packets with errors', ['hostname', 'interface'])
ib_unicast_rcv_packets = Gauge('ib_unicast_rcv_packets', 'Total number of unicast packets, including unicast packets containing errors', ['hostname', 'interface'])
ib_unicast_xmit_packets = Gauge('ib_unicast_xmit_packets', 'Total number of unicast packets transmitted on all VLs from the port. This may include unicast packets with errors', ['hostname', 'interface'])
ib_multicast_rcv_packets = Gauge('ib_multicast_rcv_packets', 'Total number of multicast packets received on all VLS from the port. This may include multicast packets with errors', ['hostname', 'interface'])
ib_multicast_xmit_packets = Gauge('ib_multicast_xmit_packets', 'Total number of multicast packets transmitted on all VLs from the port. This may include multicast packets with errors', ['hostname', 'interface'])
ib_link_downed = Gauge('ib_link_downed', 'Total number of times the Port Training state machine has failed the link error recovery process and downed the link', ['hostname', 'interface'])
ib_port_xmit_discards = Gauge('ib_port_xmit_discards', 'Total number of outbound packets discarded by the port because the port is down or congested', ['hostname', 'interface'])
ib_VL15_dropped = Gauge('ib_VL15_dropped', 'Number of incoming VL15 packets dropped due to resource limitations', ['hostname', 'interface'])
ib_port_xmit_wait = Gauge('ib_port_xmit_wait', 'The number of ticks during which the port had data to transmit but no data was sent during the entire tick (either because of insufficient credits or because of lack of arbitration)', ['hostname', 'interface'])

def get_rdma_metrics():
    hostname = subprocess.getoutput("hostname")
    rdma_nics = subprocess.getoutput("rdma link show | grep rdma | cut -d ' ' -f2 | sed 's/\/1//g' | tr '\n' ' '").split()
    for nic in rdma_nics:
        # Hardware counters for ROCEv2 Diagnostics
        ecn_packets = int(subprocess.getoutput("cat /sys/class/infiniband/{nic}/ports/1/hw_counters/np_ecn_marked_roce_packets".format(nic=nic)))
        out_of_seq = int(subprocess.getoutput("cat /sys/class/infiniband/{nic}/ports/1/hw_counters/out_of_sequence".format(nic=nic)))
        seq_err = int(subprocess.getoutput("cat /sys/class/infiniband/{nic}/ports/1/hw_counters/packet_seq_err".format(nic=nic)))
        local_ack_timeout = int(subprocess.getoutput("cat /sys/class/infiniband/{nic}/ports/1/hw_counters/local_ack_timeout_err".format(nic=nic)))
        adp_retrans = int(subprocess.getoutput("cat /sys/class/infiniband/{nic}/ports/1/hw_counters/roce_adp_retrans".format(nic=nic)))
        cnp_sent = int(subprocess.getoutput("cat /sys/class/infiniband/{nic}/ports/1/hw_counters/np_cnp_sent".format(nic=nic)))
        cnp_handled = int(subprocess.getoutput("cat /sys/class/infiniband/{nic}/ports/1/hw_counters/rp_cnp_handled".format(nic=nic)))
        cnp_ignored = int(subprocess.getoutput("cat /sys/class/infiniband/{nic}/ports/1/hw_counters/rp_cnp_ignored".format(nic=nic)))
        icrc_encaps = int(subprocess.getoutput("cat /sys/class/infiniband/{nic}/ports/1/hw_counters/rx_icrc_encapsulated".format(nic=nic)))
        slow_restart = int(subprocess.getoutput("cat /sys/class/infiniband/{nic}/ports/1/hw_counters/roce_slow_restart".format(nic=nic)))

        # Port counters for Mellanox Port Diagnostics
        link_state = int(subprocess.getoutput("cat /sys/class/infiniband/{nic}/ports/1/state".format(nic=nic)).split(':')[0])
        link_phys_state = int(subprocess.getoutput("cat /sys/class/infiniband/{nic}/ports/1/phys_state".format(nic=nic)).split(':')[0]) 
        symbol_error = int(subprocess.getoutput("cat /sys/class/infiniband/{nic}/ports/1/counters/symbol_error".format(nic=nic)))
        port_rcv_errors = int(subprocess.getoutput("cat /sys/class/infiniband/{nic}/ports/1/counters/port_rcv_errors".format(nic=nic)))
        port_rcv_remote_phsyical_errors = int(subprocess.getoutput("cat /sys/class/infiniband/{nic}/ports/1/counters/port_rcv_remote_physical_errors".format(nic=nic)))
        port_rcv_switch_relay_errors = int(subprocess.getoutput("cat /sys/class/infiniband/{nic}/ports/1/counters/port_rcv_switch_relay_errors".format(nic=nic)))
        link_error_recovery = int(subprocess.getoutput("cat /sys/class/infiniband/{nic}/ports/1/counters/link_error_recovery".format(nic=nic)))
        port_xmit_constraint_errors = int(subprocess.getoutput("cat /sys/class/infiniband/{nic}/ports/1/counters/port_xmit_constraint_errors".format(nic=nic)))
        port_rcv_contraint_errors = int(subprocess.getoutput("cat /sys/class/infiniband/{nic}/ports/1/counters/port_rcv_constraint_errors".format(nic=nic)))
        local_link_integrity_errors = int(subprocess.getoutput("cat /sys/class/infiniband/{nic}/ports/1/counters/local_link_integrity_errors".format(nic=nic)))
        excessive_buffer_overrun_errors = int(subprocess.getoutput("cat /sys/class/infiniband/{nic}/ports/1/counters/excessive_buffer_overrun_errors".format(nic=nic)))
        port_xmit_data = int(subprocess.getoutput("cat /sys/class/infiniband/{nic}/ports/1/counters/port_xmit_data".format(nic=nic)))
        port_rcv_data = int(subprocess.getoutput("cat /sys/class/infiniband/{nic}/ports/1/counters/port_rcv_data".format(nic=nic)))
        port_xmit_packets = int(subprocess.getoutput("cat /sys/class/infiniband/{nic}/ports/1/counters/port_xmit_packets".format(nic=nic)))
        port_rcv_packets = int(subprocess.getoutput("cat /sys/class/infiniband/{nic}/ports/1/counters/port_rcv_packets".format(nic=nic)))
        unicast_rcv_packets = int(subprocess.getoutput("cat /sys/class/infiniband/{nic}/ports/1/counters/unicast_rcv_packets".format(nic=nic)))
        unicast_xmit_packets = int(subprocess.getoutput("cat /sys/class/infiniband/{nic}/ports/1/counters/unicast_xmit_packets".format(nic=nic)))
        multicast_rcv_packets = int(subprocess.getoutput("cat /sys/class/infiniband/{nic}/ports/1/counters/multicast_rcv_packets".format(nic=nic)))
        multicast_xmit_packets = int(subprocess.getoutput("cat /sys/class/infiniband/{nic}/ports/1/counters/multicast_xmit_packets".format(nic=nic)))
        link_downed = int(subprocess.getoutput("cat /sys/class/infiniband/{nic}/ports/1/counters/link_downed".format(nic=nic)))
        port_xmit_discards = int(subprocess.getoutput("cat /sys/class/infiniband/{nic}/ports/1/counters/port_xmit_discards".format(nic=nic)))
        VL15_dropped = int(subprocess.getoutput("cat /sys/class/infiniband/{nic}/ports/1/counters/VL15_dropped".format(nic=nic)))
        port_xmit_wait = int(subprocess.getoutput("cat /sys/class/infiniband/{nic}/ports/1/counters/port_xmit_wait".format(nic=nic)))
        
        # Publish metrics
        np_ecn_marked_roce_packets.labels(hostname=hostname, interface=nic).set(ecn_packets)
        out_of_sequence.labels(hostname=hostname, interface=nic).set(out_of_seq)
        packet_seq_err.labels(hostname=hostname, interface=nic).set(seq_err)
        local_ack_timeout_err.labels(hostname=hostname, interface=nic).set(local_ack_timeout)
        roce_adp_retrans.labels(hostname=hostname, interface=nic).set(adp_retrans)
        np_cnp_sent.labels(hostname=hostname, interface=nic).set(cnp_sent)
        rp_cnp_handled.labels(hostname=hostname, interface=nic).set(cnp_handled)
        rp_cnp_ignored.labels(hostname=hostname, interface=nic).set(cnp_ignored)
        rx_icrc_encapsulated.labels(hostname=hostname, interface=nic).set(icrc_encaps)
        roce_slow_restart.labels(hostname=hostname, interface=nic).set(slow_restart)

        ib_link_state.labels(hostname=hostname, interface=nic).set(link_state)
        ib_link_phys_state.labels(hostname=hostname, interface=nic).set(link_phys_state)
        ib_symbol_error.labels(hostname=hostname, interface=nic).set(symbol_error)
        ib_port_rcv_errors.labels(hostname=hostname, interface=nic).set(port_rcv_errors)
        ib_port_rcv_remote_phsyical_errors.labels(hostname=hostname, interface=nic).set(port_rcv_remote_phsyical_errors)
        ib_port_rcv_switch_relay_errors.labels(hostname=hostname, interface=nic).set(port_rcv_switch_relay_errors)
        ib_link_error_recovery.labels(hostname=hostname, interface=nic).set(link_error_recovery)
        ib_port_xmit_constraint_errors.labels(hostname=hostname, interface=nic).set(port_xmit_constraint_errors)
        ib_port_rcv_contraint_errors.labels(hostname=hostname, interface=nic).set(port_rcv_contraint_errors)
        ib_local_link_integrity_errors.labels(hostname=hostname, interface=nic).set(local_link_integrity_errors)
        ib_excessive_buffer_overrun_errors.labels(hostname=hostname, interface=nic).set(excessive_buffer_overrun_errors)
        ib_port_xmit_data.labels(hostname=hostname, interface=nic).set(port_xmit_data)
        ib_port_rcv_data.labels(hostname=hostname, interface=nic).set(port_rcv_data)
        ib_port_xmit_packets.labels(hostname=hostname, interface=nic).set(port_xmit_packets)
        ib_port_rcv_packets.labels(hostname=hostname, interface=nic).set(port_rcv_packets)
        ib_unicast_rcv_packets.labels(hostname=hostname, interface=nic).set(unicast_rcv_packets)
        ib_unicast_xmit_packets.labels(hostname=hostname, interface=nic).set(unicast_xmit_packets)
        ib_multicast_rcv_packets.labels(hostname=hostname, interface=nic).set(multicast_rcv_packets)
        ib_multicast_xmit_packets.labels(hostname=hostname, interface=nic).set(multicast_xmit_packets)
        ib_link_downed.labels(hostname=hostname, interface=nic).set(link_downed)
        ib_port_xmit_discards.labels(hostname=hostname, interface=nic).set(port_xmit_discards)
        ib_VL15_dropped.labels(hostname=hostname, interface=nic).set(VL15_dropped)
        ib_port_xmit_wait.labels(hostname=hostname, interface=nic).set(port_xmit_wait)

if __name__ == '__main__':
    # Start up the server to expose the metrics.
    start_http_server(9500)
    # Generate RDMA metrics every 10 seconds
    while True:
        get_rdma_metrics()
        time.sleep(10)