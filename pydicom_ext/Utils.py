#-*- coding:utf-8 -*-
"""
    Utils

    Copyright (c) 2017 Tetsuya Shinaji

    This software is released under the MIT License.

    http://opensource.org/licenses/mit-license.php
    
    Date: 2017/02/15

"""

import numpy as np
from matplotlib import pyplot as plt
from pydicom_ext import pydicom_series
from pydicom.dataset import Dataset, FileDataset
from datetime import datetime
import os
import random
from typing import Tuple
import traceback
import json

def convert_npy_to_dicom(fname, npy_array,
                         slice_thickness=None,
                         pixel_spacing=None):
    """
    convert npy array to dicom
    :param fname: file name
    :param npy_array: npy array
    :param slice_thickness: slice thickness
    :param pixel_spacing: pixel spacing
    :return:  dcm
    """

    uint16_img = np.array(npy_array)
    uint16_img = (
        (uint16_img - uint16_img.min()) /
        (uint16_img.max() - uint16_img.min()) * (2**16 - 1)
    ).astype(np.uint16)
    dim = len(uint16_img.shape)
    if dim == 1:
        raise Exception('Cannot convert 1D array to dicom')
    elif dim == 2:
        uint16_img = uint16_img[np.newaxis, :, :]
    elif dim > 3:
        raise Exception('{}D array is not supported.'.format(dim))
    x_min = npy_array.min()
    x_max = npy_array.max()
    x_max_min = x_max - x_min
    t_max = (2**16) - 1
    slope = x_max_min / t_max
    intercept = x_min

    file_meta = Dataset()
    file_meta.MediaStorageSOPClassUID = '1.2.840.100008.5.1.4.1.1.20'
    file_meta.MediaStorageSOPInstanceUID = \
        '333.333.0.0.0.333.333333333.{}'.format(
            datetime.now().timestamp())
    file_meta.ImplementationClassUID = '0.0.0.0'
    dcm = FileDataset(fname, {}, file_meta=file_meta, preamble=b'\0' * 128)

    dcm.Modality = 'OT'
    dcm.ImageType = ['ORIGINAL', 'PRIMARY']

    dcm.ContentDate = datetime.now().strftime('%Y%m%d')
    dcm.ContentTime = datetime.now().strftime('%H%M%S')
    dcm.InstanceCreationDate = datetime.now().strftime('%Y%m%d')
    dcm.InstanceCreationTime = datetime.now().strftime('%H%M%S')
    dcm.SeriesDate = datetime.now().strftime('%Y%m%d')
    dcm.SeriesTime = datetime.now().strftime('%H%M%S')
    dcm.AcquisitionTime = datetime.now().strftime('%H%M%S')
    dcm.PatientName = os.path.basename(fname)
    dcm.PatientBirthDate = datetime.now().strftime('%Y%m%d')
    dcm.PatientAge = '000Y'
    dcm.PatientSize = 1
    dcm.PatientWeight = 1
    dcm.PatientID = os.path.basename(fname)
    dcm.PatientSex = 'O'
    dcm.StudyDescription = os.path.basename(fname)
    dcm.StudyDate = datetime.now().strftime('%Y%m%d')
    dcm.StudyTime = datetime.now().strftime('%H%M%S')
    dcm.StudyID = os.path.basename(fname)
    dcm.SeriesDescription = os.path.basename(fname)
    dcm.SamplesPerPixel = 1
    dcm.PhotometricInterpretation = 'MONOCHROME1'
    dcm.PixelRepresentation = 0  # unsigned 0, signed 1
    dcm.HighBit = 16
    dcm.BitsStored = 16
    dcm.BitsAllocated = 16
    dcm.SmallestImagePixelValue = uint16_img.min()
    dcm.LargestImagePixelValue = uint16_img.max()
    dcm.Columns = uint16_img.shape[2]
    dcm.Rows = uint16_img.shape[1]
    dcm.NumberOfFrames = uint16_img.shape[0]
    dcm.NumberOfSlices = uint16_img.shape[0]
    dcm.ImagesInAquisition = uint16_img.shape[0]
    dcm.RescaleIntercept = intercept
    dcm.RescaleSlope = slope
    dcm.SliceVector = (np.arange(uint16_img.shape[0]) + 1).tolist()
    dcm.FrameIncrementPointer = [(0x0054, 0x0080)]

    dcm.PixelData = uint16_img.tostring()
    dcm.SliceThickness = 1 if slice_thickness is None else slice_thickness
    ps = 1 if pixel_spacing is None else pixel_spacing
    if isinstance(ps, list) or isinstance(ps, np.ndarray):
        dcm.PixelSpacing = [ps[0], ps[1]]
    else:
        dcm.PixelSpacing = [ps, ps]
    dcm.InstanceCreatorUID = '333.333.0.0.0'
    dcm.SOPClassUID = '1.2.840.10008.5.1.4.1.1.20'
    dcm.SOPInstanceUID = '333.333.0.0.0.{}'.format(
        datetime.now().timestamp())
    dcm.StudyInstanceUID = '333.333.0.0.0.{}'.format(datetime.now().timestamp())
    dcm.SeriesInstanceUID = '333.333.0.0.0.{}.3333'.format(
        datetime.now().timestamp())
    dcm.FrameOfReferenceUID = dcm.StudyInstanceUID
    dcm.SeriesNumber = 0
    dcm.InstanceNumber = 0
    dcm.BodyPartExamined = 'UNKNOWN'
    dcm.Manufacturer = 'DicomConversionUtils'
    dcm.DeviceSerialNumber = ''
    dcm.AcquisitionTerminationCondition = 'MANU'
    dcm.SoftwareVersions = 'UNKNOWN'
    dcm.AccessionNumber = '{:13d}'.format(random.randint(0, 1e13))
    dcm.InstitutionName = 'DicomConversionUtils'

    dcm.save_as(fname)
    uint16_img.tofile('test.raw')
    return dcm


def convert_dicom_to_npy(dcm: pydicom_series.DicomSeries) -> \
        Tuple[np.ndarray, dict]:
    """

    :param dcm: DicomSeries
    :return: npy image data, meta data
    """

    try:
        img = dcm.get_pixel_array()
        meta_data = {}
        meta_data['StudyDescription'] = dcm.info.StudyDescription
        meta_data['SeriesDescription'] = dcm.info.SeriesDescription
        if 'AcquisitionDateTime' in dir(dcm.info):
            meta_data['AcquisitionDateTime'] = dcm.info.AcquisitionDateTime
        else:
            meta_data['AcquisitionDateTime'] = dcm.info.AcquisitionDate + \
                                               dcm.info.AcquisitionTime
        if type(meta_data['AcquisitionDateTime']) == bytes:
            meta_data['AcquisitionDateTime'] = meta_data[
                'AcquisitionDateTime'].decode('utf-8')
        meta_data['AcquisitionTime'] = dcm.info.AcquisitionTime
        meta_data['ImageOrientationPatient'] = dcm.info.ImageOrientationPatient
        meta_data['ImagePositionPatient'] = dcm.info.ImagePositionPatient
        meta_data['PatientOrientation'] = dcm.info.PatientOrientation
        meta_data['PatientPosition'] = dcm.info.PatientPosition
        meta_data['SliceThickness'] = float(
            dcm.info.SliceThickness)
        meta_data['PixelSpacing'] = np.array(
            dcm.info.PixelSpacing).astype(float).tolist()
        meta_data['ImageSize'] = img.shape
        if 'LargestImagePixelValue' in dir(dcm.info):
            meta_data['LargestImagePixelValue'] = dcm.info.LargestImagePixelValue
        if 'SmallestImagePixelValue' in dir(dcm.info):
            meta_data['SmallestImagePixelValue'] = dcm.info.SmallestImagePixelValue
        meta_data['MaxPixelValue'] = float(img.max())
        meta_data['MinPixelValue'] = float(img.min())
        if 'Units' in dir(dcm.info):
            meta_data['Units'] = dcm.info.Units
        meta_data['RescaleIntercept'] = float(
            dcm.info.RescaleIntercept)
        meta_data['RescaleSlope'] = float(dcm.info.RescaleSlope)
        meta_data['WindowCenter'] = float(dcm.info.WindowCenter)
        meta_data['WindowWidth'] = float(dcm.info.WindowWidth)
        meta_data['SeriesInstanceUID'] = dcm.info.SeriesInstanceUID
        meta_data['Modality'] = dcm.info.Modality
        if len(dcm._datasets) > 1:
            p0 = dcm._datasets[0].ImagePositionPatient[2]
            p1 = dcm._datasets[1].ImagePositionPatient[2]
            if (p1 - p0) == 0:
                raise Exception('Zero slice thickness was detected.')
            meta_data['SliceDirection'] = 1 if (p1 - p0) > 0 else -1
        if 'ActualFrameDuration' in dir(dcm.info):
            meta_data['ActualFrameDuration'] = dcm.info.ActualFrameDuration
        if 'RadiopharmaceuticalInformationSequence' in dir(
                dcm.info):
            info = \
            dcm.info.RadiopharmaceuticalInformationSequence[0]
            meta_data['Radiopharmaceutical'] = info.Radiopharmaceutical
            meta_data[
                'RadiopharmaceuticalStartTime'] = info.RadiopharmaceuticalStartTime
            meta_data['RadionuclideTotalDose'] = float(
                info.RadionuclideTotalDose)
            meta_data['RadionuclideHalfLife'] = float(
                info.RadionuclideHalfLife)
            meta_data['RadionuclidePositronFraction'] = float(
                info.RadionuclidePositronFraction)
            meta_data[
                'RadiopharmaceuticalStartDateTime'] = info.RadiopharmaceuticalStartDateTime
            if type(meta_data[
                        'RadiopharmaceuticalStartDateTime']) == bytes:
                meta_data['RadiopharmaceuticalStartDateTime'] = \
                meta_data['RadiopharmaceuticalStartDateTime'].decode(
                    'utf-8')
        return img, meta_data
    except:
        print(traceback.format_exc())

