import mne
import os
import philistine as ph
import numpy as np
import matplotlib
from matplotlib import pyplot as plt

def check_for_raws(subj,block,user,data_from_server):
	'''
	Makes sure you have all the files necessary to compare CCA to ICA data.
	'''
	blockid = subj + '_' + block
	if data_from_server:
		data_dir = '/Users/%s/Box/onsetProd/' % (user)
	else:
		data_dir = '/home/%s/data/' % (user)
	ds_fname = data_dir + 'eeg/' + subj + '/' + blockid + '/%s_downsampled.vhdr' % blockid
	ica_fname = data_dir + 'eeg/' + subj + '/' + blockid + '/%s_ica.fif' % blockid
	cca_fname = data_dir + 'eeg/' + subj + '/' + blockid + '/%s_cca.vhdr' % blockid
	# check if the files exist
	if not os.path.isfile(ica_fname):
		raise Exception("%s does not exist." % ica_fname)
	if not os.path.isfile(cca_fname):
		raise Exception("%s does not exist." % cca_fname)
	return data_dir, ds_fname, ica_fname, cca_fname
def get_reject_onsets():
	'''
	Returns the onset of rejected segments as timestamps so that you can
	re-reject those segments in the CCA'd data.
	This needs to be done for CCA AND(?) CCA_nofilt data!!
	'''
	# print the onsets of BAD_ segments from ica.fif
	ica_fname = "FILE PATH HERE"
	ica_raw = mne.io.read_raw_fif(ica_fname, preload=True)
	print("Here is a list of your onsets of rejected segments.")
	for annotation in ica_raw.annotations:
		if annotation['description'] == 'BAD_':
			print(annotation['onset'])
	# then do raw.plot
	rdy = input("Press enter when you are ready to reject these segments in your CCA'd data.")
	cca_fname = 'FILE PATH HERE'
	cca_raw = mne.io.read_raw_brainvision(cca_fname, preload=True)
	cca_raw.plot
	# then overwrite the old one with the annotations yay
	# I FROGET HWOT O DO THIS LOL
def fif_to_vhdr(subj,block,user,data_from_server):
	'''
	converts ica.fif and ica_nofilt.fif to .vhdr
	for the purpose of loading into EEGLAB
	'''
	blockid = subj + '_' + block
	if data_from_server:
		data_dir = '/Users/%s/Box/onsetProd/eeg/' % (user)
	else:
		data_dir = '/home/%s/data/eeg/' % (user)
	# get paths
	ica_fname = data_dir + subj + '/' + blockid + '/%s_ica.fif' % blockid
	vhdr_fname = data_dir + subj + '/' + blockid + '/%s_ica.vhdr' % blockid
	# load raw
	raw = mne.io.read_raw_fif(ica_fname, preload=True)
	print("HPF at 0.16Hz...")
	raw.filter(l_freq=0.16,h_freq=None)
	# convert
	ph.mne.write_raw_brainvision(raw, vhdr_fname)
	print("Done!")
def plot_emg_pre_post_cca(subj, block, data_dir, bads=[], tmin=-0.3, tmax=1.5, plot_image=True, subplots=False):
	blockid = subj + '_' + block
	eegpath = data_dir + 'eeg/' + subj + '/' + blockid + '/' + blockid
	ica_f = eegpath + '_ica.fif'
	cca_f = eegpath + '_cca.vhdr'
	if subj not in ['OP0001','OP0002']:
		raw_orig=mne.io.read_raw_fif(ica_f,preload=True,verbose=False)
		raw_orig.set_eeg_reference(['TP9','TP10'])
		raw_orig.notch_filter(60)
		raw_orig.set_channel_types({'vEOG': 'eog', 'hEOG':'emg'}) # For some reason cant plot the EOG images themselves if they are MISC

		raw_cca=mne.io.read_raw_brainvision(cca_f,preload=True) 

		jaw_emg_events = mne.preprocessing.find_eog_events(raw_orig, ch_name='hEOG')  

		orig_emg_epochs = mne.Epochs(raw_orig, jaw_emg_events, event_id=998, tmin=tmin, tmax=tmax) # default value for eog      
		cca_emg_epochs = mne.Epochs(raw_cca, jaw_emg_events, event_id=998, tmin=tmin, tmax=tmax)  
		if len(bads) > 0:
			bads_in_raw = []
			for bad in bads:
				if bad in raw_cca.info['ch_names']:
					bads_in_raw.append(bad)
			bads = bads_in_raw
		picks = mne.pick_types(raw_cca.info, meg=False, eeg=True, exclude='bads')
		print([raw_cca.info['ch_names'][i] for i in picks])

		if plot_image == True:
			orig_emg_epochs.plot_image(combine='mean',picks=picks, vmin=-150, vmax=150)
			cca_emg_epochs.plot_image(combine='mean',picks=picks, vmin=-150, vmax=150)

		orig_emg_data = orig_emg_epochs.get_data(picks=picks)
		cca_emg_data = cca_emg_epochs.get_data(picks=picks)
		times = orig_emg_epochs.times

		if subplots == False:
			plt.figure()
		plt.fill_between(times, orig_emg_data.mean(1).mean(0)+orig_emg_data.mean(1).std(0)/np.sqrt(orig_emg_data.shape[0]), y2=orig_emg_data.mean(1).mean(0)-orig_emg_data.mean(1).std(0)/np.sqrt(orig_emg_data.shape[0]), alpha=0.5)
		plt.plot(times, orig_emg_data.mean(1).mean(0), label='ICA')
		plt.fill_between(times, cca_emg_data.mean(1).mean(0)+cca_emg_data.mean(1).std(0)/np.sqrt(cca_emg_data.shape[0]), y2=cca_emg_data.mean(1).mean(0)-cca_emg_data.mean(1).std(0)/np.sqrt(cca_emg_data.shape[0]), alpha=0.5)
		plt.plot(times, cca_emg_data.mean(1).mean(0), label='post CCA')
		plt.axvline(0)
		plt.axhline(0)
		plt.xlabel('Time since onset of EMG (s)')
		plt.ylabel('V')
		plt.title(blockid)
		plt.legend()
		
		return orig_emg_data, cca_emg_data, times
	else:
		print("Subj %s doesn't have EMG elecs so skipping." % subj)
		orig_emg_data = []
		cca_emg_data = []
		times = []
		return orig_emg_data, cca_emg_data, times
def plot_emg_all_three(subj, block, data_dir, bads=[], tmin=-0.3, tmax=1.5, plot_image=False, subplots=True):
	blockid = subj + '_' + block
	eegpath = data_dir + 'eeg/' + subj + '/' + blockid + '/' + blockid
	ds_f = eegpath + '_downsampled.vhdr'
	ica_f = eegpath + '_ica.fif'
	cca_f = eegpath + '_cca.vhdr'

	raw_ds = mne.io.read_raw_brainvision(ds_f,preload=True,verbose=False)
	if subj == 'OP0017':
		raw_ds.info['bads']=['TP9']
		raw_ds.interpolate_bads(reset_bads=False)
	raw_ds.set_eeg_reference(['TP9','TP10'])
	raw_ds.notch_filter(60)
	raw_ds.set_channel_types({'vEOG': 'eog', 'hEOG':'emg'}) # For some reason cant plot the EOG images themselves if they are MISC
	raw_ds.filter(l_freq=1,h_freq=15)

	raw_orig=mne.io.read_raw_fif(ica_f,preload=True,verbose=False)
	raw_orig.set_channel_types({'vEOG': 'eog', 'hEOG':'emg'}) # For some reason cant plot the EOG images themselves if they are MISC
	raw_orig.filter(l_freq=1,h_freq=15)

	raw_cca=mne.io.read_raw_brainvision(cca_f,preload=True,verbose=False)
	raw_cca.filter(l_freq=1,h_freq=15)

	jaw_emg_events = mne.preprocessing.find_eog_events(raw_ds, ch_name='hEOG')  

	ds_emg_epochs = mne.Epochs(raw_ds,jaw_emg_events,event_id=998, tmin=tmin, tmax=tmax)
	orig_emg_epochs = mne.Epochs(raw_orig, jaw_emg_events, event_id=998, tmin=tmin, tmax=tmax) # default value for eog      
	cca_emg_epochs = mne.Epochs(raw_cca, jaw_emg_events, event_id=998, tmin=tmin, tmax=tmax)  
	
	if len(bads) > 0:
		bads_in_raw = []
		for bad in bads:
			if bad in raw_cca.info['ch_names']:
				bads_in_raw.append(bad)
		bads = bads_in_raw
	picks = mne.pick_types(raw_cca.info, meg=False, eeg=True, exclude='bads')
	print([raw_cca.info['ch_names'][i] for i in picks])

	if plot_image == True:
		ds_emg_epochs.plot_image(combine='mean',picks=picks, vmin=-150, vmax=150)
		orig_emg_epochs.plot_image(combine='mean',picks=picks, vmin=-150, vmax=150)
		cca_emg_epochs.plot_image(combine='mean',picks=picks, vmin=-150, vmax=150)

	ds_emg_data = ds_emg_epochs.get_data(picks=picks)
	orig_emg_data = orig_emg_epochs.get_data(picks=picks)
	cca_emg_data = cca_emg_epochs.get_data(picks=picks)
	times = ds_emg_epochs.times

	if subplots == False:
		plt.figure()
	plt.fill_between(times, ds_emg_data.mean(1).mean(0)+ds_emg_data.mean(1).std(0)/np.sqrt(ds_emg_data.shape[0]), y2=ds_emg_data.mean(1).mean(0)-ds_emg_data.mean(1).std(0)/np.sqrt(ds_emg_data.shape[0]), color='deepskyblue', alpha=0.5)
	plt.plot(times, ds_emg_data.mean(1).mean(0), label='raw', color='deepskyblue')
	plt.fill_between(times, orig_emg_data.mean(1).mean(0)+orig_emg_data.mean(1).std(0)/np.sqrt(orig_emg_data.shape[0]), y2=orig_emg_data.mean(1).mean(0)-orig_emg_data.mean(1).std(0)/np.sqrt(orig_emg_data.shape[0]), color='darkorchid', alpha=0.5)
	plt.plot(times, orig_emg_data.mean(1).mean(0), label='ICA', color='darkorchid')
	plt.fill_between(times, cca_emg_data.mean(1).mean(0)+cca_emg_data.mean(1).std(0)/np.sqrt(cca_emg_data.shape[0]), y2=cca_emg_data.mean(1).mean(0)-cca_emg_data.mean(1).std(0)/np.sqrt(cca_emg_data.shape[0]), color='limegreen', alpha=0.5)
	plt.plot(times, cca_emg_data.mean(1).mean(0), label='post CCA', color='limegreen')
	plt.axvline(0)
	plt.axhline(0)
	plt.xlabel('Time since onset of EMG (s)')
	plt.ylabel('V')
	plt.title(blockid)
	plt.legend()
	
	return ds_emg_data,orig_emg_data,cca_emg_data,ds_emg_epochs,orig_emg_epochs,cca_emg_epochs,raw_cca.info,times



