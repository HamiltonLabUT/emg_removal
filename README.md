# emg_removal

Code for reproducing the results from Kurteff et al. "Removal of EMG Artifact from EEG During Naturalistic Speech Production" (submitted to NeuroImage). Article PDF can be found [here](https://github.com/HamiltonLabUT/emg_removal/blob/main/Kurteffetal2021EMGSubmitted.pdf).

Data available on [OSF](https://osf.io/fnrd9/).

Below is a breakdown of different files in this repo:

## `analysis`
This folder contains code for reproducing figures and statistical analyses from the manuscript.
* `artifacts.ipynb` -- code for producing Figure 1 from the manuscript.
* `methods_figures.ipynb` -- code for producing Figures 2 and 3 from the manuscript.
* `raw_cca_stats.ipynb` -- code for creating `./r/lmem_dwemg_paper.csv`
* `jaw_emg_wilcoxon.ipynb` -- code for analyzing manually-annotated EMG epochs in a single subject (OP0008).
* `./r/cca_lmem.ipynb` -- R code for running the linear mixed-effects model reported in the manuscript.

## `preprocessing`
This folder contains code for preprocessing raw EEG data. CCA correction was performed in EEGLab using settings outlined in the manuscript, but all other preprocessing was accomplished through these scripts. If you do not wish to run these scripts, you can download the preprocessed datasets (or the raw ones) from the OSF repository.
* `cca_utils.py` -- functions for preprocessing and visualizing data using MNE-python.
* `convert_fif_to_vhdr.py` -- wrapper script for philistine that converts an MNE-created .fif file to .vhdr for use in EEGLab.
*  `ica.py` -- script meant to be ran in an interactive Python shell for doing ICA. Uses MNE-python's ICA functions as a backend. You will need to manually edit some paths in this script if you are running this script.

## `task`
This folder contains mostly Swift code for running the perception-production task on an iPad during data collection.
* `sampling_MOCHA.ipynb` -- Python notebook that describes how the subset of MOCHA used in the task was sampled.


## Third-party software used
* [philistine](https://pypi.org/project/philistine/)
* [EEGLab](https://sccn.ucsd.edu/eeglab/index.php)
* [AAR plugin for EEGLab](https://germangh.github.io/eeglab_plugin_aar/)
* [MNE-python](https://mne.tools/dev/index.html)
