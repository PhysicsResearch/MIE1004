"""Plot the axial, coronal and sagittal views of one CT series (MIE1004 lab, Chapter 4).

Example code for the extra challenge: read all slices of one CT series, sort
them, put them in a 3D NumPy array and show the middle slice in each direction.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pydicom

# Change this to the folder of one CT series on your computer, for example:
# r"C:\Users\yourname\Desktop\tcia_data\nsclc_radiomics\LUNG1-001\2008-09-18-69331\0-82046"
DATA_FOLDER = r"path\to\one\CT\series\folder"


def read_volume(folder):
    """Read all slices in `folder`. Return them as a 3D array, plus the display aspect ratio."""
    folder = Path(folder)
    if not folder.is_dir():
        raise SystemExit(f"Folder not found: {folder}\nSet DATA_FOLDER at the top of the script.")

    # Read all files, including the images.
    files = list(folder.glob("*.dcm"))
    slices = [pydicom.dcmread(file) for file in files]

    # The file names don't follow the slice order, so sort the slices by InstanceNumber.
    # If it is not available, sort by the z position (the third value of
    # ImagePositionPatient), from the highest z (the head) to the lowest.
    if all("InstanceNumber" in ds for ds in slices):
        slices.sort(key=lambda ds: int(ds.InstanceNumber))
    else:
        slices.sort(key=lambda ds: float(ds.ImagePositionPatient[2]), reverse=True)

    # Dimensions and number type of the 3D array.
    n_slices = len(slices)
    n_rows = slices[0].Rows
    n_columns = slices[0].Columns
    dtype = slices[0].pixel_array.dtype

    # Set up an empty 3D array and fill it, one slice at a time.
    volume = np.zeros((n_slices, n_rows, n_columns), dtype=dtype)
    for i, ds in enumerate(slices):
        volume[i, :, :] = ds.pixel_array

    # Slices are further apart (SliceThickness) than pixels within a slice (PixelSpacing),
    # so the coronal and sagittal views need this aspect ratio to not look squashed.
    aspect = float(slices[0].SliceThickness) / float(slices[0].PixelSpacing[0])
    return volume, aspect


def plot_views(volume, aspect):
    """Show the middle axial, coronal and sagittal slice next to each other."""
    n_slices, n_rows, n_columns = volume.shape
    axial = volume[n_slices // 2, :, :]
    coronal = volume[:, n_rows // 2, :]
    sagittal = volume[:, :, n_columns // 2]

    fig, axes = plt.subplots(1, 3, figsize=(12, 5))
    axes[0].imshow(axial, cmap="gray")
    axes[0].set_title("Axial")
    axes[1].imshow(coronal, cmap="gray", aspect=aspect)
    axes[1].set_title("Coronal")
    axes[2].imshow(sagittal, cmap="gray", aspect=aspect)
    axes[2].set_title("Sagittal")
    for ax in axes:
        ax.axis("off")
    fig.tight_layout()
    plt.show()


def main():
    volume, aspect = read_volume(DATA_FOLDER)
    print(f"Read {volume.shape[0]} slices of {volume.shape[1]} x {volume.shape[2]} pixels ({volume.dtype})")
    plot_views(volume, aspect)


if __name__ == "__main__":
    main()
