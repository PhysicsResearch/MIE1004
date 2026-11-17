"""Plot the axial, coronal and sagittal views of one CT series (MIE1004 lab, Chapter 4).

Example code for the extra challenge: read all slices of one CT series, sort
them, stack them into a 3D NumPy array and show the middle slice in each direction.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pydicom

# Change this to the folder of one CT series on your computer, for example:
# r"C:\Users\yourname\Desktop\tcia_data\nsclc_radiomics\LUNG1-001\2008-09-18-69331\0-82046"
DATA_FOLDER = r"path\to\one\CT\series\folder"


def read_volume(folder):
    """Read all slices in `folder` and return them as a 3D array, plus the display aspect ratio."""
    folder = Path(folder)
    if not folder.is_dir():
        raise SystemExit(f"Folder not found: {folder}\nSet DATA_FOLDER at the top of the script.")

    slices = [pydicom.dcmread(file) for file in folder.glob("*.dcm")]

    # The file names don't follow the slice order, so sort the slices by InstanceNumber.
    # If it is missing, sort by the z position of the slice (the third value of
    # ImagePositionPatient), from the highest z (the head) to the lowest.
    if all("InstanceNumber" in s for s in slices):
        slices.sort(key=lambda s: int(s.InstanceNumber))
    else:
        slices.sort(key=lambda s: float(s.ImagePositionPatient[2]), reverse=True)

    volume = np.stack([s.pixel_array for s in slices])  # shape: (slices, rows, columns)

    # Slices are further apart (SliceThickness) than pixels within a slice (PixelSpacing),
    # so the coronal and sagittal views need this aspect ratio to not look squashed.
    aspect = float(slices[0].SliceThickness) / float(slices[0].PixelSpacing[0])
    return volume, aspect


def plot_views(volume, aspect):
    """Show the middle axial, coronal and sagittal slice next to each other."""
    n_slices, n_rows, n_columns = volume.shape
    views = [
        ("Axial", volume[n_slices // 2, :, :], 1),
        ("Coronal", volume[:, n_rows // 2, :], aspect),
        ("Sagittal", volume[:, :, n_columns // 2], aspect),
    ]

    fig, axes = plt.subplots(1, 3, figsize=(12, 5))
    for ax, (name, image, ratio) in zip(axes, views):
        ax.imshow(image, cmap="gray", aspect=ratio)
        ax.set_title(name)
        ax.axis("off")
    fig.tight_layout()
    plt.show()


def main():
    volume, aspect = read_volume(DATA_FOLDER)
    print(f"Read {volume.shape[0]} slices of {volume.shape[1]} x {volume.shape[2]} pixels")
    plot_views(volume, aspect)


if __name__ == "__main__":
    main()
