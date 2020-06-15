# -*- coding: utf-8 -*-

from openpyxl import Workbook, load_workbook
import pandas as pd

# Open the excel sheets with the selected images for download
filename  ="F:/Postdoc 2020-2024/Projects/Graslandonderzoek/2. Methodology/Part 1 - Creating time series/C - Planet data/Image lists/Planet_imgs_Turnhout_2018.xlsx"
wb = load_workbook(filename)

# Extract values from this sheet
data = wb['imgs_min_deviat'].values

# Get the first line in file as a header line
columns = next(data)[0:]

# Create a DataFrame based on the second and subsequent lines of data
sel_imgs = pd.DataFrame(data, columns=columns)
sel_imgs = sel_imgs.iloc[1:]

# Select only the first image (first line of Dataframe)
first_im = sel_imgs.iloc[0:1]       

# Download this image clipped to the study area

                 