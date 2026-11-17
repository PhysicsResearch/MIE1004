"""Read metadata from DICOM files (MIE1004 lab, Chapter 3).

Step 5: read_metadata() reads the metadata of the DICOM files in all
subfolders of the data folder. get_demographics() collects the sex and age
of each patient, and plot_demographics() shows them in a graph.
make_report() summarises and checks the dataset.
"""

import time
from pathlib import Path

import matplotlib.pyplot as plt
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


def plot_demographics(demographics, filename="demographics.png"):
    """Plot the number of patients per sex and the age of each patient, and save the graph."""
    fig, (ax_sex, ax_age) = plt.subplots(1, 2, figsize=(10, 4))

    counts = demographics["Sex"].value_counts()
    ax_sex.bar(counts.index, counts.values)
    ax_sex.set_title("Patients per sex")
    ax_sex.set_ylabel("Number of patients")

    known = demographics.dropna(subset=["Age"])  # patients without an age are left out
    ax_age.bar(known["PatientID"], known["Age"])
    ax_age.set_title(f"Age per patient ({len(known)} of {len(demographics)} known)")
    ax_age.set_ylabel("Age (years)")
    ax_age.tick_params(axis="x", rotation=45)

    fig.tight_layout()
    fig.savefig(filename)
    print(f"Saved the graph as {filename}")
    plt.show()


def make_report(table, folder, filename="report.txt"):
    """Summarise the dataset, check that each patient folder holds one patient, and save it."""
    lines = [
        "Dataset report",
        f"Folder: {folder}",
        f"Patient folders: {table['PatientFolder'].nunique()}",
        f"Files: {len(table)}",
        "",
        "Files per patient folder:",
    ]
    for patient_folder, count in table.groupby("PatientFolder").size().items():
        lines.append(f"  {patient_folder}: {count}")

    lines += ["", "Modalities (number of files):"]
    for modality, count in table["Modality"].value_counts().items():
        lines.append(f"  {modality}: {count}")

    lines += ["", "One patient per folder:"]
    for patient_folder, files in table.groupby("PatientFolder"):
        patient_ids = sorted(files["PatientID"].unique())
        result = "OK" if len(patient_ids) == 1 else "PROBLEM"
        lines.append(f"  {patient_folder}: {result} (PatientID: {', '.join(patient_ids)})")

    report = "\n".join(lines)
    print(report)
    Path(filename).write_text(report + "\n", encoding="utf-8")
    print(f"Saved the report as {filename}")


def main():
    pd.set_option("display.max_columns", None)  # show all columns of the table
    pd.set_option("display.width", 200)

    start = time.perf_counter()
    table = read_metadata(DATA_FOLDER)
    print(f"Read {len(table)} files in {time.perf_counter() - start:.2f} s")

    make_report(table, DATA_FOLDER)

    demographics = get_demographics(table)
    print(demographics)
    plot_demographics(demographics)


if __name__ == "__main__":
    main()
