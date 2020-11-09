from giscovid import fetch_current_datetime, fetch_current_data
import os
import sys

csv_outdir = "dataset"

def build_output_path(dt):
    return os.path.join(csv_outdir, dt.strftime("%Y%m%d_%H%M.csv"))

if __name__ == "__main__":
    if not os.path.isdir(csv_outdir):
        os.makedirs(csv_outdir)
    
    dt = fetch_current_datetime()
    outfile = build_output_path(dt)

    if not os.path.isfile(outfile):
        # else, new data, store it!
        print(f"Fetching new data [{dt}]")
        df = fetch_current_data()
        df.to_csv(outfile, index_label="id_comune")
        sys.exit(0)
    sys.exit(1)
