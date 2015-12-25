import os

import pyshark
import numpy as np
from math import cos,sin,pi
from datetime import datetime

# acronyms
# Nr: number of rows in V matrix, equal to num of Space-Time streams, corresponds to number of beamformer (AP) antennas.
# Nc: number of columns in V matrix, <= Min(Nr, beamformee antennas)
# Ng: number of subcarriers grouped together and for which a single V matrix is used
# Na: number of angles in V matrix
# Ns: number of subcarriers in a report

angles_order = {}
subcarriers = {}

def handle_pcap(pcap_filename):
	cap = pyshark.FileCapture(pcap_filename)
	matricies = []
	for p in cap:
		if p.wlan.fc_subtype == '14' and p.wlan.fc_type == '0':
			matricies.append(compute_matrices_from_report(p))

def extract_mimo_control_params(p):
	#see page 54 in 802.11ac-2013
	Nc = int(p.layers[3].wlan_vht_mimo_control_nrindex[-1], 16) + 1
	Nr = int(p.layers[3].wlan_vht_mimo_control_ncindex, 16) + 1
	chanwidth = 2**(int(p.layers[3].wlan_vht_mimo_control_chanwidth, 16) + 1) * 10
	Ng = 2**int(p.layers[3].wlan_vht_mimo_control_grouping, 16)
	codebook = int(p.layers[3].wlan_vht_mimo_control_codebookinfo, 16)
	feedbacktype = int(p.layers[3].wlan_vht_mimo_control_feedbacktype, 16) # 0: SU-MIMO, 1: MU-MIMO
	reminaing_segments = int(p.layers[3].wlan_vht_mimo_control_remainingfeedbackseg, 16)
	is_first_segment = int(p.layers[3].wlan_vht_mimo_control_firstfeedbackseg, 16)
	sounding_token_number = int(p.layers[3].wlan_vht_mimo_control_soundingdialogtocketnbr, 16)

	report = p.layers[3].wlan_vht_compressed_beamforming_report.split(':')

	return Nc, Nr, chanwidth, Ng, codebook, feedbacktype, reminaing_segments, is_first_segment, sounding_token_number,\
				 report

def compute_matrices_from_report(p):

	Nc, Nr, chanwidth, Ng, codebook, feedbacktype, reminaing_segments, is_first_segment, sounding_token_number, report\
		= extract_mimo_control_params(p)

	#if feedback is not Multi User or if not the first segment of the feedback report (special case of big reports)
	if feedbacktype != 1 or is_first_segment != 1:
		print 'something is fishy...'


	Na, angles = angles_order[(Nr, Nc)]
	psi_bits, phi_bits = get_angles_bits(feedbacktype, codebook)
	subcarrier_v_matrix_size = Na*(psi_bits+phi_bits) / 2
	subcarriers_of_V_matrices = subcarriers[(chanwidth, Ng)]
	Ns = len(subcarriers_of_V_matrices)

	# read avg_SNR for space-time stream from 1 to Nc
	avg_SNR = []
	for i in range(Nc):
		snr_byte = report.pop(0)
		avg_SNR.append(extract_SNR_from_report(snr_byte))

	binary_report = ''
	for report_byte in report:
		binary_report += bin(int(report_byte, 16))[2:].zfill(8)


	v_matrices = []
	for first_bit in range(0, len(binary_report), subcarrier_v_matrix_size):
		v_matrix = compute_subcarrier_matrix(binary_report[first_bit:first_bit+subcarrier_v_matrix_size], psi_bits,
																				 phi_bits, angles, Nr, Nc)
		v_matrices.append(v_matrix)

	return v_matrices, avg_SNR

def compute_subcarrier_matrix(binary_str, psi_bits, phi_bits, angles, Nr, Nc):
	v_matrix = np.identity(Nr)
	for phi_psi_couple in angles:

		phi_matrix = np.identity(Nr)
		for phi in phi_psi_couple[0]:
			phi_val = extract_phi_angle(binary_str[:phi_bits], phi_bits)
			binary_str = binary_str[phi_bits:] # "pop" the used bits
			phi_index = phi[0] - 1
			phi_matrix[phi_index, phi_index] = np.exp(1j*phi_val)

		v_matrix *= phi_matrix


		# this code creates the psi givens rotation matricies already TRANSPOSED!!!!
		for psi in phi_psi_couple[1]:
			psi_matrix = np.identity(Nr)
			psi_val = extract_psi_angle(binary_str[:psi_bits], psi_bits)
			binary_str = binary_str[psi_bits:] # "pop" the used bits
			sin_psi = sin(psi_val)
			cos_psi = cos(psi_val)
			psi_i = psi[0] - 1
			psi_j = psi[1] - 1
			psi_matrix[psi_i, psi_i] = cos_psi
			psi_matrix[psi_j, psi_j] = cos_psi
			psi_matrix[psi_i, psi_j] = sin_psi
			psi_matrix[psi_j, psi_i] = -sin_psi
			v_matrix *= psi_matrix

	v_matrix *= np.eye(Nr, Nc)

	return v_matrix

# angle quantization is described in 802.11ac-2013 p. 57
def extract_phi_angle(phi_binary_reversed, phi_bits):
	return (int(phi_binary_reversed[::-1], 2) * pi) / 2**(phi_bits-1) + (pi / 2**phi_bits)

def extract_psi_angle(psi_binary_reversed, psi_bits):
	return (int(psi_binary_reversed[::-1], 2) * pi) / 2**(psi_bits+1) + (pi / 2**(psi_bits+2))

# create angles order.
# indexes below are (row,col) in a matrix
# The format is of couples (phi, psi), where phi is a list of indexes (i,j) representing the indexes of phi in a single
# matrix, while psi is a list of indexes (k,l), where each couple (k,l) represents a different identity matrix with
# values inserted to the indexes (kk, kl, lk, ll) so: (cos(psi), -sin(psi), sin(psi), cos(psi))
#
# angles list is partial since Linksys EA8500 has only 4 antennas. The rest can be found in 802.11ac-2013 spec, p. 55-57
#
# also creates the list of subcarriers for which V matrices are stored in the report. key: (chanwidth, Ng)
# this is a partial list since Linksys EA8500 use only channel width of 20, 40, and maybe 80.
# The rest can be found in 802.11ac-2013 spec, p. 59-63
def create_angles_and_sub_carriers():
	# angles_order[(2,1)] = [(('phi', (1, 1)), ('psi', (2, 1)))]
	angles_order[(2,1)] = (2, [(((1, 1),), ((2, 1),))])
	angles_order[(2,2)] = angles_order[(2,1)]

	angles_order[(3,1)] = (4, [(((1, 1), (2, 1)), ((2, 1), (3, 1)))])
	angles_order[(3,2)] = (6, angles_order[(3,1)][1] + [(((2, 2),), ((3, 2),))])
	angles_order[(3,3)] = angles_order[(3,2)]

	angles_order[(4,1)] = (6, [(((1, 1), (2, 1), (3, 1)), ((2, 1), (3, 1), (4, 1)))])
	angles_order[(4,2)] = (10, angles_order[(4,1)][1] + [(((2, 2), (3, 2)), ((3, 2), (4, 2)))])
	angles_order[(4,3)] = (12, angles_order[(4,2)][1] + [(((3, 3),), ((4, 3),))])
	angles_order[(4,4)] = angles_order[(4,3)]

	subcarriers[(20, 1)] = [x for x in range(-28, 29, 1) if x not in [-21, -7, 0, 7, 21]]
	subcarriers[(20, 2)] = range(-28, 0, 2) + [-1, 1] + range(2, 29, 2)
	subcarriers[(20, 3)] = range(-28, 0, 4) + [-1, 1] + range(4, 29, 4)

	subcarriers[(40, 1)] = [x for x in range(-58, 59, 1) if x not in [-53, -25, -11, -1,  0, 1, 11, 25, 53]]
	subcarriers[(40, 2)] = [x for x in range(-58, 59, 2) if x not in [0,]]
	subcarriers[(40, 3)] = range(-58, 59, 4)

	subcarriers[(80, 1)] = [x for x in range(-122, 123, 1) if x not in [-103, -75, -39, -11, -1,  0, 1, 11, 25, 75, 103]]
	subcarriers[(80, 2)] = [x for x in range(-122, 123, 2) if x not in [0,]]
	subcarriers[(80, 3)] = range(-122, 123, 4)

# output: (psi_bits, phi_bits) the number of bits used to represent psi and phi
def get_angles_bits(mimo_feedbacktype, mimo_codebook):
	if mimo_feedbacktype == 0: #SU-MIMO
		return {
			0: (2,4),
			1: (4,6),
			}[mimo_codebook]
	elif mimo_feedbacktype == 1: #MU-MIMO
		return {
			0: (5,7),
			1: (7,9),
			}[mimo_codebook]


# -128 equals snr of <=-10 dB , and every value above increase by 0.25 (e.g. -127 = -9.75 dB)
def extract_SNR_from_report(snr_byte):
	db_val = (int(snr_byte, 16) + 128.0) * 0.25 - 10.0

	return db_val


def extract_events(pcap_path):
	cap = pyshark.FileCapture(pcap_path)
	events = []
	before_first_sounding = True


	for packet_i, p in enumerate(cap):

		#skip packets before first sounding
		if before_first_sounding:
			if not is_sounding(p):
				continue

		if is_sounding(p):
			if before_first_sounding:
				before_first_sounding = False
			else:
				events.append([sounding_stats, beamforming_report, downstream_packets_stats])
			sounding_stats = (datetime.fromtimestamp(extract_time(p)), packet_i + 1)
			downstream_packets_stats = []

		elif is_report(p):
			beamforming_report = extract_beamforming_report(p)
		elif is_downstream(p):
			downstream_packets_stats.append(extract_downstream_stats(p))

	return events

def is_sounding(p):
	return is_packet(p, '1', '5')

def is_report(p):
	return is_packet(p, '0', '14')

def is_downstream_data(p):
	pass

def is_downstream(p):
	pass

def is_packet(p, type, subtype):
	return  p.wlan.fc_type == type and p.wlan.fc_subtype == subtype

def extract_time(p):
	return float(p.sniff_timestamp)

def extract_beamforming_report(p):
	return compute_matrices_from_report(p)

def extract_downstream_stats(p):
	pass

def merge_events(all_events):
	pass

def save_chronological_events(chronological_events):
	pass


def merge_pcaps_to_chronological_events(pcacp_dir_path='resources/pcap_to_synch/'):
	pcap_filenames = os.listdir(pcacp_dir_path)
	all_events = []
	for filename in pcap_filenames:
		pcap_events = extract_events(pcacp_dir_path + filename)
		all_events.append(pcap_events)

	chronological_events = merge_events(all_events)
	save_chronological_events(chronological_events)

if __name__ == '__main__':
	create_angles_and_sub_carriers()
	# filename = '/Users/uriklarman/Professional/Neo/code/neo/MU_MIMO/PCAP/resources/wcap/interesting.pcap'
	# handle_pcap(filename)

	merge_pcaps_to_chronological_events()

	print 'done'