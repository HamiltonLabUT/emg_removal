# ica.py
# by Garret Kurteff, for the Hamilton Lab
# June 2019
# Only works in Python 3.x due to use of input() over raw_input().

# imports
from mne.preprocessing import create_eog_epochs, create_ecg_epochs
from mne.preprocessing import ICA
from mne.time_frequency import tfr_morlet as tfr_morlet
import numpy as np
import os # for raw_input
import matplotlib
matplotlib.rcParams['backend'] = 'TKAgg'
from matplotlib import pyplot as plt
import mne

def str2bool(v):
	return v.lower() in ("yes", "true", "t", "1")

# File paths
user = 'kfsh'
eeg_data_path = '/home/%s/data/eeg/' % user # Path to your EEG data
montage_path = '/home/%s/git/onsetProd/eeg/montage/AP-128.bvef' % user
# user = 'liberty'
# eeg_data_path = '/Users/%s/Box/onsetProd/eeg/' % (user) # Path to your EEG data
# montage_path = '/Users/liberty/Documents/Austin/code/EventDetection/montage/AP-128.bvef' 

# Get inputs
print("What subject?")
subj = input("> ")
if subj == 'OP0002':
	block = 'B2'
else:
	block = 'B1'
blockid = subj + "_" + block
print("Have you annotated your data already (aka, does '%s_downsampled_with_annotations.fif' exist?" % blockid)
annotated = str2bool(input("> "))

# Load the raw and reference/resample if necessary
if annotated == True:
	data_suffix = 'downsampled_with_annotations.fif'
	fname = "%s%s/%s/%s_%s" % (eeg_data_path, subj, blockid, blockid, data_suffix)
	raw = mne.io.read_raw_fif(fname, preload=True)
elif annotated == False:
	data_suffix = 'downsampled.vhdr'
	fname = "%s%s/%s/%s_%s" % (eeg_data_path, subj, blockid, blockid, data_suffix)
	raw = mne.io.read_raw_brainvision(fname, preload=True)
	# Concatenate second block for these subjects
	mtpl_blocks = ['OP0015','OP0016','OP0020']
	if subj in mtpl_blocks:
		print('Reading in raw from second block.')
		fname_b2 = "%s%s/%s_B2/%s_B2_%s" % (eeg_data_path, subj, subj, subj, data_suffix)
		raw_b2 = mne.io.read_raw_brainvision(fname_b2, preload=True)
		print('Concatenating raw across blocks.')
		raw = mne.concatenate_raws([raw,raw_b2], preload=True)
	# Set the montage
	# For newer versions of MNE (0.19+) you have to do it like this
	# mne.channels.read_custom_montage(montage_path, unit='mm')
	# For older versions (0.17, 0.18), you do it like this:
	print("Applying montage...")
	raw.set_montage(montage_path)
	# Resample to 128 Hz
	if raw.info['sfreq'] != 128.:
		print("Resampling raw (This should never run lol, wtf)")
		raw.resample(128.)
	# code for messing with OP0017 as TP9 is bad for that participant.
	# We fix this by interpolating TP9 and then referencing from it and TP10.
	# Visual inspection of data on 10-4-19 shows it's pretty good.
	if subj == "OP0017" and annotated == False:
		print("Interpolating bad reference for %s..." % blockid)
		raw.info['bads'] = ['TP9']
		raw.interpolate_bads(reset_bads=False)
	# Re-reference to average of the mastoids
	if annotated == False:
		if subj != 'OP0014':
			print("Applying linked mastoid reference...")
			raw.set_eeg_reference(['TP9','TP10'])
		else:
			print("Will reference to linked mastoids after ICA for %s." % subj)
else:
	raise Exception("Could not find file %s." % fname)

# Look at PSD
picks = mne.pick_types(raw.info, eeg=True, meg=False, eog=False)
raw.plot_psd(picks=picks)

# Filter the data (notch 60 and bandpass 1-30)
if annotated == False:
	print("Notch filtering data...")
	raw.notch_filter(60)
	print("Band pass filtering data 1-30Hz...")
	raw.filter(l_freq=1,h_freq=30) 

# Annotate raw
print("Press Enter to look at raw data... or type 'skip' to skip this step.")
skip = input("> ")
if skip != 'skip':
	raw.plot()
print("Press Enter when you are finished annotating the raw data... ")
input("> ")

# save raw with annotations in case of a crash
if annotated == False:
	raw.save('%s%s/%s_%s/%s_%s_downsampled_with_annotations.fif'%(eeg_data_path, subj, subj, block, subj, block), overwrite=True)
	print("Annotated raw saved!")

# Ok let's do the ICA now
print("Press Enter to continue to ICA... ")
input("> ")

# Get the EEG channels
picks = mne.pick_types(raw.info, eeg=True, meg=False, eog=False)

# Fit ICA on the EEG channels
ica = ICA(n_components=len(picks), method='infomax')
ica.fit(raw, picks=picks, reject_by_annotation=True)

# Find epochs where EOG is large
if 'vEOG' in raw.ch_names:
	eog_epochs = create_eog_epochs(raw, ch_name='vEOG', tmin=-0.5, tmax=0.5, l_freq=1, h_freq=10) 
	if len(eog_epochs) > 0:
		eog_inds, scores = ica.find_bads_eog(eog_epochs, ch_name='vEOG', threshold=3.0)
		if len(eog_inds) > 0:
			ica.plot_properties(eog_epochs, picks=eog_inds)
			print("Press Enter to plot all components...")
			input("> ")
	else:
		print("No EOG components found. Well that sucks lol. Hopefully you can fix this in the future somehow.")
else:
	print("You don't have vEOG! So skipping this step...")

# Inspect components
ica.plot_components()
print("Press Enter to plot sources...")
input("> ")
ica.plot_sources(raw)
print("Press Enter to plot properties of first 5 components...")
input("> ")
ica.plot_properties(raw)
print("Press Enter to reject components... ")
input("> ")
ica.plot_components()

# Apply ICA
print("Press Enter to apply ICA to data...")
input("> ")
# Reload the raw
ds_fname = "%s%s/%s/%s_downsampled.vhdr" % (eeg_data_path, subj, blockid, blockid)
reloaded_raw = mne.io.read_raw_brainvision(ds_fname, preload=True)
mtpl_blocks = ['OP0015','OP0016','OP0020']
if subj in mtpl_blocks:
	print('Reading in raw from second block.')
	ds_fname_b2 = "%s%s/%s_B2/%s_B2_downsampled.vhdr" % (eeg_data_path, subj, subj, subj)
	reloaded_raw_b2 = mne.io.read_raw_brainvision(ds_fname_b2, preload=True)
	print('Concatenating raw across blocks.')
	reloaded_raw = mne.concatenate_raws([reloaded_raw,reloaded_raw_b2], preload=True)
# Re-preprocess raw data before you apply ICA, except for bandpass filtering AND montage!
if reloaded_raw.info['sfreq'] != 128.:
	reloaded_raw.resample(128.)
if subj == "OP0017":
	reloaded_raw.info['bads'] = ['TP9']
	reloaded_raw.interpolate_bads(reset_bads=False)
# Re-reference to average of the mastoids
reloaded_raw.set_eeg_reference(['TP9','TP10'])
reloaded_raw.notch_filter(60)
ica.apply(reloaded_raw)
ica.apply(raw)

# Filter even lower and then plot original raw
print("ICA applied! Band pass filtering 1-15 for visual inspection of applied ICA...")
raw.filter(l_freq=1,h_freq=15)
# Look at raw again to see if ICA is good
print("Press Enter to look at raw again to see if ICA was good... ")
input("> ")
raw.plot()

print("Remember, if you are going to load in this ica.fif file, you will need to do your bandpass filter (1-15 Hz) and re-apply your montage first.")
reloaded_raw.save('%s%s/%s_%s/%s_%s_ica.fif'%(eeg_data_path, subj, subj, block, subj, block), overwrite=True)