"""Read metadata from DICOM files (MIE1004 lab, Chapter 3).

Step 1: read_metadata() reads every DICOM file in one folder and collects
several tags of each file in a table. main() prints the table.
"""

from pathlib import Path

import pandas as pd
import pydicom

# Change this to the folder of one CT series on your computer, for example:
# r"C:\Users\yourname\Desktop\tcia_data\nsclc_radiomics\LUNG1-001\2008-09-18-69331\0-82046"
DATA_FOLDER = r"path\to\one\CT\series\folder"

# The tags to collect from each file. print(ds) shows all the tags of a file.
TAGS = ["PatientID", "Modality", "Manufacturer", "AcquisitionDate", "SliceThickness", "Rows", "Columns"]


def read_metadata(folder):
    """Read every DICOM file in `folder` and return a table with one row per file."""
    folder = Path(folder)
    if not folder.is_dir():
        raise SystemExit(f"Folder not found: {folder}\nSet DATA_FOLDER at the top of the script.")

    files = sorted(folder.glob("*.dcm"))
    print(f"Found {len(files)} DICOM files in {folder}")

    rows = []
    for file in files:
        ds = pydicom.dcmread(file)  # read the whole file
        image = ds.pixel_array  # the image of this slice, as a NumPy array
        row = {tag: ds.get(tag, "missing") for tag in TAGS}
        rows.append(row)
    return pd.DataFrame(rows)


def main():
    pd.set_option("display.max_columns", None)  # show all columns of the table
    pd.set_option("display.width", 200)

    table = read_metadata(DATA_FOLDER)
    print(table)


if __name__ == "__main__":
    main()
