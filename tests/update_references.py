"""Script to update/add reference files for regression tests."""
from datetime import datetime
from pathlib import Path

import pandas as pd

import NewareNDA

nda_path = Path(r"tests\nda")
ref_paths = {
    "chg": Path(r"tests\reference"),
    "dchg": Path(r"tests\reference_cycle_mode_dchg"),
    "auto": Path(r"tests\reference_cycle_mode_auto"),
}

if __name__ == "__main__":
    for nda in nda_path.rglob("*.nda*"):
        for cycle_mode in ["chg", "dchg", "auto"]:
            df = NewareNDA.read(nda, cycle_mode=cycle_mode)
            ref_path = (ref_paths[cycle_mode] / nda.with_suffix(".ftr").name).resolve()

            # If it doesn't exist yet, add it
            if not ref_path.exists():
                print(f"ADDING {nda.stem} {cycle_mode}")
                df.to_feather(ref_path)
                continue

            ref_df = pd.read_feather(ref_path)
            # Convert dates to timestamps for comparison
            test_df = df.copy()
            test_df["Timestamp"] = test_df["Timestamp"].apply(datetime.timestamp)
            ref_df["Timestamp"] = ref_df["Timestamp"].apply(datetime.timestamp)
            try:
                pd.testing.assert_frame_equal(test_df, ref_df, check_like=True)
            except AssertionError:
                # If it doesn't match, update
                print(f"UPDATING {nda.stem} {cycle_mode}")
                df.to_feather(ref_path)
                continue

            print(f"Unchanged: {nda.stem} {cycle_mode}")

