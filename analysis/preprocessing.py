#!/usr/bin/env python
# from gkTools.preprocessing import preprocessing

"""
preprocessing.py (formerly eegTools)
Created by Garret Kurteff for Liberty Hamilton's Lab
Abridged for EMG removal paper
v1.3
6/27/2021
"""

# imports - may need to be cleaned up
import csv
import numpy as np
import scipy.io
import scipy.io.wavfile
from scipy.io.wavfile import read
import scipy.signal
import scipy.stats
import mne
import math
from fuzzywuzzy import fuzz
from glob import glob
from matplotlib import cm
from matplotlib import pyplot as plt
import h5py
import os
from logging import warning
import re
from tqdm import tqdm
from timeit import default_timer as timer
from pydub import AudioSegment
from pathlib import Path
import ast
plt.rcParams['figure.facecolor'] = 'white'

# HELPER FUNCTIONS
def find_subjs(data_path, mode='eeg', data_suffix=None):
	subjs = []
	if data_suffix != None:
		path = data_path + '%s/*/*/*'%mode + data_suffix
		print(path)
	else:
		path = data_path + '%s/*'%mode
	for subj in glob(path):
		if 'OP' in subj:
			# print(subj)
			for i,char in enumerate(subj):
				if char == 'O' and '/' not in subj[i:]:
					# print(subj[i:i+6])
					subjs.append(subj[i:i+6])
	subjs.sort()
	print("Found the following subjs:")
	print(subjs)
	return subjs
def get_bads(subj,git_path):
	'''
	Returns bad EEG channels from a text file.
	'''
	bads_txt = git_path + '/emg_removal/eeg/bads.txt'
	with open(bads_txt, 'r') as f:
		contents = f.read()
		dictionary = ast.literal_eval(contents)
	bads = dictionary[subj]
	return bads
def find_blocks(subj, data_path, mode='ecog',print=False):
	'''
	Find block names using glob.
	Returns block names as a list.
	'''
	blocks = []
	path = data_path + mode + '/' + subj + '/*'
	for block in glob(path):
		if print==True:
			print("Found these blocks:")
			print(block)
		if mode == 'ecog':
			for i,s in enumerate(block):
				if s == 'B':
					if block[i:i+3]!='Box':
						blocks.append(block[i:i+3])
			blocks = [s.replace('/', '') for s in blocks]
		if mode == 'eeg':
			blocks.append(block[-2:])
	return(blocks)
def get_event_fnames(subj, block, channel, git_path, mode='eeg'):
	'''
	Returns a list of event filenames.
	'''
	blockid = subj + '_' + block
	event_fnames = []
	event_fname = '%s/emg_removal/analysis/eventfiles/%s/%s/%s_%s_ph_all.txt' % (git_path, mode, subj, blockid, blockid, channel)
	event_fnames.append(event_fname)
	event_fname = '%s/emg_removal/analysis/eventfiles/%s/%s/%s_%s_ph_el.txt' % (git_path, mode, subj, blockid, blockid, channel)
	event_fnames.append(event_fname)
	event_fname = '%s/emg_removal/analysis/eventfiles/%s/%s/%s_%s_ph_sh.txt' % (git_path, mode, subj, blockid, blockid, channel)
	event_fnames.append(event_fname)
	event_fname = '%s/emg_removal/analysis/eventfiles/%s/%s/%s_%s_sn_all.txt' % (git_path, mode, subj, blockid, blockid, channel)
	event_fnames.append(event_fname)
	event_fname = '%s/emg_removal/analysis/eventfiles/%s/%s/%s_%s_sn_el.txt' % (git_path, mode, subj, blockid, blockid, channel)
	event_fnames.append(event_fname)
	event_fname = '%s/emg_removal/analysis/eventfiles/%s/%s/%s_%s_sn_sh.txt' % (git_path, mode, subj, blockid, blockid, channel)
	event_fnames.append(event_fname)
	return(event_fnames)

# AUDIO PREPROCESSING FUNCTIONS
def butter_highpass(cutoff, fs, order=5):
	'''
	Creates a high pass filter at a given frequency.
	'''
	nyq = 0.5 * fs
	normal_cutoff = cutoff / nyq
	b, a = scipy.signal.butter(order, normal_cutoff, btype='high', analog=False)
	return b, a
def butter_highpass_filter(data, cutoff, fs, order=2):
	'''
	Highpass filters data using a highpass filter.
	'''
	b, a = butter_highpass(cutoff, fs, order=order)
	y = scipy.signal.filtfilt(b, a, data,axis=0)
	return y

# EEG PREPROCESSING FUNCTIONS
def interpolate_bads(subj,block,raw,git_path,data_path):
	'''
	Used on CCA data to get raws of n<64 channels up to 64.
	Makes plotting stuff easier.
	* raw: instance of cca data that is missing channels.
	FILTER FIRST!
	'''
	blockid = subj + '_' + block
	# Load OP0001 for reasons
	OP0001_fpath = data_path + 'eeg/OP0001/OP0001_B1/OP0001_B1_cca.vhdr'
	OP0001_raw = mne.io.read_raw_brainvision(OP0001_fpath,preload=True,verbose=False)
	OP0001_info = OP0001_raw.info
	chs = OP0001_info['ch_names']
	bads = get_bads(subj,git_path)
	if len(bads) > 0:
		# if the bad channel is still in our raw we can just interpolate it
		bads_in_raw = []
		for bad in bads:
			if bad in raw.info['ch_names']:
				bads_in_raw.append(bad)
		if len(bads_in_raw) > 0:
			raw.info['bads'] = bads_in_raw
			print("Interpolating %r" % raw.info['bads'])
			raw.interpolate_bads()
		# if the bad channel isn't in our raw then we need to copy it over from
		# the pre-CCA'd data to interpolate it
		# AKA what will be happening most of the time.
		else:
			pre_cca_raw_path = '%seeg/%s/%s/%s_downsampled_with_annotations.fif' % (
			data_path,subj,blockid,blockid)
			pre_cca_raw = mne.io.read_raw_fif(
				pre_cca_raw_path,preload=True,verbose=False)
	#                     pre_cca_raw.pick_types(meg=False,eeg=True,eog=False)
			print(blockid, 'CCA BADS: ',blockid,bads)
			print(blockid, 'PRE CCA BADS: ',pre_cca_raw.info['bads'])
			nsamps = raw.get_data().shape[1]
			new_data = []
			# loop through all 64 chans and find which are missing
			for ch in chs: 
				if ch not in raw.info['ch_names']: # if it's missing
					# make zeros array with same shape as one channel
					channel_to_be_interpolated = np.zeros((1,nsamps))
					new_data.append(channel_to_be_interpolated)
				else:
					# get data from cca, append to list
					channel_from_cca = raw.get_data(picks=ch)
					new_data.append(np.array(channel_from_cca[0]))
			# Concatenate all the channels and use it to make a 64 channel Raw
			# use OP0001 info because it has 64 chans
			raw = mne.io.RawArray(np.vstack(new_data),OP0001_info)
			# Set the bads from the CCA info
			raw.info['bads'] = bads
			# Interpolate the bads (the np.zeros)
			raw.interpolate_bads()
	else:
		print(blockid, "has no bads.")
	return raw
def get_event_file(subj, block, channel, level, condition, git_path, mode='eeg'):
	'''
	Returns a specific filename from a list of event filenames
	given a level of representation (phoneme, sentence)
	and a task condition (echolalia, shuffled, all).
	'''
	event_fnames = get_event_fnames(subj,block,channel,git_path,mode=mode)
	if level == "phoneme":
		fnames = [0,1,2]
	elif level == "sentence":
		fnames = [3,4,5]
	else:
		print("Couldn't retrieve event filename as an unsupported level (%s) was specified." % level)
	if condition == "all":
		event_fname = event_fnames[fnames[0]]
	elif condition == "echolalia":
		event_fname = event_fnames[fnames[1]]
	elif condition == "shuffled":
		event_fname = event_fnames[fnames[2]]
	else:
		raise Exception(
			"Couldn't retrieve event filename as an unsupported level (%s) or unsupported task condition (%s) was specified." % (level, condition))
	return(event_fname)

