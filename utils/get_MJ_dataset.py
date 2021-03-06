"""

Runs training for deepInsight

"""
# -----------------------------------------------------------------------

from deep_insight.options import get_opts, MODEL_PATH, H5_PATH, LOSS_WEIGHTS, LOSS_FUNCTIONS
from deep_insight.wavelet_dataset import create_train_and_test_datasets, WaveletDataset
from deep_insight.trainer import Trainer
import deep_insight.loss
import deep_insight.networks
import os
import matplotlib.pyplot as plt
import h5py
import numpy as np
import torch
import wandb
import matplotlib.pyplot as plt
from ratSLAM.input import MattJonesDummyInput, MattJonesInput

# -----------------------------------------------------------------------

if torch.cuda.is_available():
    DEVICE = torch.device("cuda")
else:
    DEVICE = torch.device("cpu")


#PREPROCESSED_HDF5_PATH = './data/processed_R2478.h5'
PREPROCESSED_HDF5_PATH = H5_PATH
hdf5_file = h5py.File(PREPROCESSED_HDF5_PATH, mode='r')
wavelets = np.array(hdf5_file['inputs/wavelets'])
loss_functions = LOSS_FUNCTIONS

loss_weights = LOSS_WEIGHTS
# ..todo: second param is unneccecary at this stage, use two empty arrays to match signature but it doesn't matter
training_options = get_opts(PREPROCESSED_HDF5_PATH, train_test_times=(np.array([]), np.array([])))
training_options['loss_functions'] = loss_functions.copy()
training_options['loss_weights'] = loss_weights
training_options['loss_names'] = list(loss_functions.keys())
training_options['shuffle'] = False

exp_indices = np.arange(0, wavelets.shape[0] - training_options['model_timesteps'])
cv_splits = np.array_split(exp_indices, training_options['num_cvs'])

training_indices = []
for arr in cv_splits[0:-1]:
    training_indices += list(arr)
training_indices = np.array(training_indices)

test_indeces = np.array(cv_splits[-1])
# opts -> generators -> model
# reset options for this cross validation set
training_options = get_opts(PREPROCESSED_HDF5_PATH, train_test_times=(training_indices, test_indeces))
training_options['loss_functions'] = loss_functions.copy()
training_options['loss_weights'] = loss_weights
training_options['loss_names'] = list(loss_functions.keys())
training_options['shuffle'] = False
training_options['random_batches'] = False

train_dataset, test_dataset = create_train_and_test_datasets(training_options, hdf5_file)
dataset = []

for t in test_dataset:
    d = t[0]
    labels = [t_2 for t_2 in t[1]]
    #dataset.append( MattJonesDummyInput( (d, labels) ) )
    dataset.append( MattJonesInput( (d, labels) ) )

def get_mj_dataset():
    return dataset
