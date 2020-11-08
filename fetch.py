from time import sleep
from giscovid import fetch_current_datetime, fetch_current_data
import os

csv_outdir = "dataset"
delay = 3600 * 1 # make periodic checks (every 1 hour)

def build_output_path(dt):
    return os.path.join(csv_outdir, dt.strftime("%Y%m%d_%H%M.csv"))

if __name__ == "__main__":
    if not os.path.isdir(csv_outdir):
        os.makedirs(csv_outdir)
    
    while True:
        dt = fetch_current_datetime()
        outfile = build_output_path(dt)

        if not os.path.isfile(outfile):
            # else, new data, store it!
            print(f"Fetching new data [{dt}]")
            df = fetch_current_data()
            df.to_csv(outfile, index_label="id_comune")

        sleep(delay)
