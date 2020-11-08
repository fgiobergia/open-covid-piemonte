from datetime import datetime
from giscovid import fetch_data_from_files
from fetch import build_output_path

if __name__ == "__main__":

    previous_data = [
        (datetime(2020, 11, 6, 11, 0), "import_data/in_1106.dat", "import_data/va_1106.dat")
    ]

    for dt, in_fname, va_fname in previous_data:
        df = fetch_data_from_files(in_fname, va_fname, dt)
        df.to_csv(build_output_path(dt), index_label="id_comune")
        print(f"Generated file for {dt}")
