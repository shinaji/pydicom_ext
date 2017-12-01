#-*- coding:utf-8 -*-
"""
    VtkDataUtils

    Copyright (c) 2017 Tetsuya Shinaji

    This software is released under the MIT License.

    http://opensource.org/licenses/mit-license.php
    
"""

import numpy as np
from matplotlib import pyplot as plt
import vtk
from typing import List, Tuple
from vtk.util import numpy_support

npy_dtype_to_vtk_dtype = {

    np.dtype(np.uint8): vtk.VTK_UNSIGNED_CHAR,
    np.dtype(np.uint16): vtk.VTK_UNSIGNED_SHORT,
    np.dtype(np.uint32): vtk.VTK_UNSIGNED_INT,
    np.dtype(np.uint64): vtk.VTK_UNSIGNED_LONG_LONG,
    np.dtype(np.uint): vtk.VTK_UNSIGNED_LONG_LONG,
    np.dtype(np.int8): vtk.VTK_CHAR,
    np.dtype(np.int16): vtk.VTK_SHORT,
    np.dtype(np.int32): vtk.VTK_INT,
    np.dtype(np.int64): vtk.VTK_LONG_LONG,
    np.dtype(np.int): vtk.VTK_LONG_LONG,
    np.dtype(np.float32): vtk.VTK_FLOAT,
    np.dtype(np.float64): vtk.VTK_DOUBLE,
    np.dtype(np.float): vtk.VTK_DOUBLE,

}


def load_vtk_file(filename: str) -> Tuple[np.ndarray, vtk.vtkStructuredPoints]:
    """

    :param filename: filename
    :return: img(npy format), img(vtk format)
    """
    reader = vtk.vtkStructuredPointsReader()
    reader.SetFileName(filename)
    reader.Update()
    vtk_img = reader.GetOutput().GetPointData().GetScalars()
    shape = np.array(reader.GetOutput().GetDimensions())
    img = numpy_support.vtk_to_numpy(vtk_img).reshape(shape[::-1])
    return img, reader.GetOutput()

def load_vtp_as_vtk_image(
        poly_data_fname: str,
        ref_vtk_img: vtk.vtkImageData,
        roi_value: int=255) -> Tuple[np.ndarray, vtk.vtkStructuredPoints]:
    """
    load  vtk poly data file as vtk image data
    :param poly_data_fname: filename
    :param ref_vtk_img: reference vtk image data
    :param roi_value: roi value
    :return: img(npy format), img(vtk format)
    """

    reader = vtk.vtkXMLPolyDataReader()
    reader.SetFileName(poly_data_fname)
    reader.Update()
    whiteImage = vtk.vtkImageData()
    whiteImage.SetSpacing(ref_vtk_img.GetSpacing())
    whiteImage.SetDimensions(ref_vtk_img.GetDimensions())
    whiteImage.SetExtent(ref_vtk_img.GetExtent())
    whiteImage.SetOrigin(ref_vtk_img.GetOrigin())
    whiteImage.AllocateScalars(vtk.VTK_UNSIGNED_CHAR, 1)
    tmp = np.ones(ref_vtk_img.GetDimensions()[::-1], dtype=np.uint8) * roi_value
    whiteImage.GetPointData().SetScalars(numpy_support.numpy_to_vtk(
        tmp.flatten(),
        deep=True,
        array_type=vtk.VTK_INT
    ))

    pol2stenc = vtk.vtkPolyDataToImageStencil()
    pol2stenc.SetInputData(reader.GetOutput())
    pol2stenc.SetOutputOrigin(ref_vtk_img.GetOrigin())
    pol2stenc.SetOutputSpacing(ref_vtk_img.GetSpacing())
    pol2stenc.SetOutputWholeExtent(whiteImage.GetExtent())
    pol2stenc.Update()

    imgstenc = vtk.vtkImageStencil()
    imgstenc.SetInputData(whiteImage)
    imgstenc.SetStencilConnection(pol2stenc.GetOutputPort())
    imgstenc.ReverseStencilOff()
    imgstenc.SetBackgroundValue(0)
    imgstenc.Update()

    vtk_img = imgstenc.GetOutput()
    img = numpy_support.vtk_to_numpy(
        vtk_img.GetPointData().GetScalars()
    ).reshape(vtk_img.GetDimensions()[::-1])


    return img, vtk_img


def save_npy_as_vtk_data(filename:str,
                         origin: [np.ndarray, Tuple, List],
                         spacing: [np.ndarray, Tuple, List],
                         npy_img: np.ndarray,
                         vti_mode: bool=False):
    """
    save numpy data with vtk format
    :param filename: filename
    :param origin: image origin coordinate [x, y, z]
    :param spacing: image spacing [x, y, z]
    :param npy_img: numpy data
    :param vti_mode: if True, save with vti format
    :return:
    """
    vtk_img = vtk.vtkImageData()
    vtk_img.SetSpacing(spacing)
    vtk_img.SetOrigin(origin)
    vtk_img.SetDimensions(np.array(npy_img.shape)[[2, 1, 0]])
    vtk_img.GetPointData().SetScalars(numpy_support.numpy_to_vtk(
        npy_img.flatten(),
        deep=True,
        array_type=npy_dtype_to_vtk_dtype[npy_img.dtype]
    ))
    vtk_img.SetExtent([
        0, npy_img.shape[2]-1,
        0, npy_img.shape[1]-1,
        0, npy_img.shape[0]-1,
    ])

    if vti_mode:
        writer = vtk.vtkXMLImageDataWriter()
        writer.SetInputData(vtk_img)
        writer.SetFileName(filename)
        writer.Update()
        writer.Write()
    else:
        writer = vtk.vtkStructuredPointsWriter()
        writer.SetInputData(vtk_img)
        writer.SetFileName(filename)
        writer.Write()
