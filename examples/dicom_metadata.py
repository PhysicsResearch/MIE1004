"""Read metadata from DICOM files (MIE1004 lab, Chapter 3).

Step 3: read_metadata() reads the metadata of the DICOM files in all
subfolders of the data folder. get_demographics() collects the sex and age
of each patient. main() prints them.
"""

import time
from pathlib import Path

import pandas as pd
import pydicom

# Change this to the top folder of your download: the folder that contains the patient
# folders, for example:
# r"C:\Users\yourname\Desktop\tcia_data\nsclc_radiomics"
DATA_FOLDER = r"path\to\your\download\folder"

# The tags to collect from each file. print(ds) shows all the tags of a file.
TAGS = [
    "PatientID", "PatientSex", "PatientAge", "Modality", "Manufacturer",
    "AcquisitionDate", "SliceThickness", "Rows", "Columns",
]


def read_metadata(folder):
    """Read every DICOM file below `folder` and return a table with one row per file."""
    folder = Path(folder)
    if not folder.is_dir():
        raise SystemExit(f"Folder not found: {folder}\nSet DATA_FOLDER at the top of the script.")

    files = sorted(folder.rglob("*.dcm"))  # all DICOM files in all subfolders
    print(f"Found {len(files)} DICOM files in {folder}")

    rows = []
    for file in files:
        ds = pydicom.dcmread(file, stop_before_pixels=True)  # read only the metadata, not the image
        row = {tag: ds.get(tag, "missing") for tag in TAGS}
        row["PatientFolder"] = file.relative_to(folder).parts[0]  # the top-level folder of this file
        rows.append(row)
    return pd.DataFrame(rows)


def age_in_years(age):
    """Turn a DICOM age such as "083Y" into a number (83), or None if it is missing."""
    if isinstance(age, str) and age.endswith("Y") and age[:-1].isdigit():
        return int(age[:-1])
    return None


def get_demographics(table):
    """Return a table with the sex and age of each patient.

    Not every file has these tags (for example RTSTRUCT files leave the sex empty),
    so use the first file of each patient that has a value.
    """
    patients = []
    for patient_id, files in table.groupby("PatientID"):
        sexes = files["PatientSex"][files["PatientSex"].isin(["M", "F", "O"])]
        ages = files["PatientAge"].map(age_in_years).dropna()
        patients.append({
            "PatientID": patient_id,
            "Sex": sexes.iloc[0] if len(sexes) > 0 else "missing",
            "Age": int(ages.iloc[0]) if len(ages) > 0 else None,
        })
    # "Int64" keeps the ages as whole numbers and shows missing ages as <NA>.
    return pd.DataFrame(patients).astype({"Age": "Int64"})


def main():
    pd.set_option("display.max_columns", None)  # show all columns of the table
    pd.set_option("display.width", 200)

    start = time.perf_counter()
    table = read_metadata(DATA_FOLDER)
    print(f"Read {len(table)} files in {time.perf_counter() - start:.2f} s")

    demographics = get_demographics(table)
    print(demographics)


if __name__ == "__main__":
    main()
