import FWQPBO
import numpy as np
try:
    import dicom
except ImportError:
    import pydicom as dicom
import scipy.io
import os
import time
from os.path import join as pjoin

cwd = os.getcwd()


def getScore(case, dir):
    # Read reconstructed DICOM-file
    recFF = np.array([])
    for file in os.listdir(dir):
        try:
            dcm = dicom.read_file(os.path.join(dir, file))
        except:
            raise Exception('File not found: {}'.format(file))
        reScaleSlope = dcm[0x00281053].value / 100  # FF in %
        recFF = np.concatenate(
            (recFF, dcm.pixel_array.transpose().flatten() * reScaleSlope))
    recFF.shape = recFF.shape + (1,)
    # Read reference MATLAB-file
    refFile = pjoin(cwd, 'challenge', 'refdata.mat')
    try:
        mat = scipy.io.loadmat(refFile)
    except:
        raise Exception('Could not read MATLAB file {}'.format(refFile))
    refFF = mat['REFCASES'][0, case - 1]
    mask = mat['MASKS'][0, case - 1]
    # Calculate score
    score = 100 * \
        (1 - np.sum((np.abs(refFF - recFF) > 0.1) * mask) / np.sum(mask))
    return score

if not os.path.isfile(pjoin(cwd, 'challenge', 'refdata.mat')):
    url = r'"https://dl.dropboxusercontent.com/u/5131732/' + \
        r'ISMRM_Challenge/refdata.mat"'
    raise Exception(r'Please download ISMRM 2012 challenge reference data '
                    'from {} and put in "challenge" subdirectory'.format(url))

modelParamsFile = pjoin(cwd, 'modelParams.txt')
cases = [1, 2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]

for case in cases[1:2]:
    if not os.path.isfile(pjoin(
            cwd, 'challenge', '{}.mat'.format(str(case).zfill(2)))):
        url = r'"http://dl.dropbox.com/u/5131732/' + \
            r'ISMRM_Challenge/data_matlab.zip"'
        raise Exception(
            r'Please download ISMRM 2012 challenge datasets from {} '
            r'and put in "challenge" subdirectory'.format(url))

results = []
for case in cases:
    dataParamsFile = pjoin(cwd, 'challenge', '{}.txt'.format(case))
    if case == 9:
        algoParamsFile = pjoin(cwd, 'algoParams2D.txt')
    else:
        algoParamsFile = pjoin(cwd, 'algoParams3D.txt')
    if not os.path.isfile(dataParamsFile):
        raise ValueError(
            "dataParamsFile not found at: {}".format(dataParamsFile))
    if not os.path.isfile(algoParamsFile):
        raise ValueError(
            "algoParamsFile not found at: {}".format(algoParamsFile))
    outDir = pjoin(cwd, 'challenge', '{}_REC'.format(str(case).zfill(2)))
    t = time.time()
    FWQPBO.FW(dataParamsFile, algoParamsFile, modelParamsFile, outDir)
    results.append((case,
                    getScore(case, pjoin(outDir, 'ff')), time.time() - t))

print()
for case, score, recTime in results:
    print('Case {}: score {}% in {} sec'.format(
        case, round(score, 2), round(recTime, 1)))
