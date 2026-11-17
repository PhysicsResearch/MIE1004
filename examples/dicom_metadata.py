"""Read metadata from DICOM files (MIE1004 lab, Chapter 3).

Starting code: read_metadata() reads every DICOM file in one folder and
collects the acquisition date of each file. main() prints the dates.
"""

from pathlib import Path

import pydicom

# Change this to the folder of one CT series on your computer, for example:
# r"C:\Users\yourname\Desktop\tcia_data\nsclc_radiomics\LUNG1-001\2008-09-18-69331\0-82046"
DATA_FOLDER = r"path\to\one\CT\series\folder"


def read_metadata(folder):
    """Read every DICOM file in `folder` and return a list of acquisition dates."""
    folder = Path(folder)
    if not folder.is_dir():
        raise SystemExit(f"Folder not found: {folder}\nSet DATA_FOLDER at the top of the script.")

    files = sorted(folder.glob("*.dcm"))
    print(f"Found {len(files)} DICOM files in {folder}")

    dates = []
    for file in files:
        ds = pydicom.dcmread(file)  # read the whole file
        image = ds.pixel_array  # the image of this slice, as a NumPy array
        dates.append(ds.get("AcquisitionDate", "missing"))
    return dates


def main():
    dates = read_metadata(DATA_FOLDER)
    for date in dates:
        print(date)


if __name__ == "__main__":
    main()
