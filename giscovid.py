import pandas as pd
from datetime import datetime
import requests
import struct
import re

def _unpack(buf, size, el_type):
    """
    Unpack an array using struct's iter_unpack.

    Arguments:
    buf: the buffer from which the array will be extracted
    size: the number of elements to be extracted
    el_type: element type (must be in `fmt_map`)

    Returns:
    unpacked: a list of values of type `el_type`
    offset: the number of bytes read from `buf`
    """
    fmt_map = {
        "int32": ("<I",4), # 4 bytes signed int, litte endian
        "float32": ("<f",4), # 4 bytes float, little endian
    }
    if el_type not in fmt_map:
        raise Exception(f"el_type should be one of {fmt_map.keys()}")
    fmt, tp_size = fmt_map[el_type]

    # iter_unpack's items are 1-tuples -- hence the v[0]
    unpacked = [ v[0] for v in struct.iter_unpack(fmt, buf[:size*tp_size]) ]
    return unpacked, size*tp_size

def _comune_id(i):
    """
    Convert `i` into a 6-digits, 0-padded string,
    compliant with ISTAT codes
    """
    return str(i).zfill(6)

def _get_cols(cols_string):
    _, _, *cols = cols_string.split(";")
    return cols

def _get_header(base_url):
    """
    Retrieve the header string (containing the number
    of municipalities and the name of the columns

    Arguments:
    base_url: the base url to contact
    returns: 
    cols: a list of all columns available 
    """
    url = f"{base_url}/va.dat"
    r = requests.get(url)
    if r.status_code != 200:
        raise Exception("Cannot retrieve header")

    return _get_cols(r.content.decode())

def _load_header(fname):
    with open(fname) as f:
        return _get_cols(f.read())

def _load_data(fname):
    with open(fname, "rb") as f:
        return f.read()
    
def _get_data(base_url):
    """
    Retrieve the data regarding the cases for each
    municipality (both in absolute terms, and for
    every 1,000 inhabitants)

    Arguments:
    base_url: the base url to contact
    returns: 
    blob: a binary string that needs to be decoded
    """
    url = f"{base_url}/in.dat"
    r = requests.get(url)
    if r.status_code != 200:
        raise Exception("Cannot retrieve data")
    return r.content

def _get_datetime(base_url):
    url = f"{base_url}/config.json"
    """
    Retrieve the datetime object from a config.json
    file (which contains a message to be displayed on
    the dashboard -- hence we will need to do some parsing

    Arguments:
    base_url: the base url to contact

    Returns:
    dt: a datetime for the correct day/month
    """

    r = requests.get(url)
    if r.status_code != 200:
        raise Exception("Cannot retrieve data")

    obj = r.json()
    update_reg = r"aggiornati alle ore (?P<hour>\d{1,2}).(?P<minute>\d{2}) del (?P<day>\d{1,2})[^\d](?P<month>\d{1,2})[^\d](?P<year>\d{4})"
    match = re.search(update_reg, obj["ultimo_aggiornamento"])
    if not match:
        raise Exception("Cannot fetch date/time from config.json")

    dt = datetime(year=int(match.group("year")),
                  month=int(match.group("month")),
                  day=int(match.group("day")),
                  hour=int(match.group("hour")),
                  minute=int(match.group("minute")))
    return dt



def _parse_data(buf, cols, dt, comuni):
    """
    Parse the data obtained from the various get_*
    functions to produce a DataFrame with the information
    about cases

    Arguments:
    buf:    a blob returned by get_data() (contains info about
            municipality ids and cases
    cols:   the number of columns contained in `buf` (should
            have length 2 and we are not going to use it --
            but still passing it for possible future needs)
    dt:     a datetime object with the date/time info of the 
            latest update
    comuni: a DataFrame with the mapping comune_id -> name

    Returns:
    df: a pandas DataFrame with columns (datetime, denominazione, 
        positivi, positivi_1000) and index comune_id

    """

    num_comuni = len(comuni)
    # the first 4 * 1181 bytes contain the municipalities'
    # codes (stored in `comuni_id_list`)
    comuni_id_list, offset = _unpack(buf, num_comuni, "int32")

    # the following 4 * 1181 * 2 bytes contain the tuple
    # (#cases, #cases/1000 ppl) for each municipality (stored in `values`)
    values, _ = _unpack(buf[offset:], num_comuni * len(cols), "float32") # 

    # making some assumptions on the columns (expecting 2)
    if len(cols) != 2:
        raise Exception(f"Expecting 2 columns, found {len(cols)}")

    cid_index = [ _comune_id(cid) for cid in comuni_id_list ]
    cols = ["denominazione", "datetime", "positivi", "positivi_1000"]
    df = pd.DataFrame(columns=cols, index=cid_index)

    entries = []
    for i in range(num_comuni):
        cid = _comune_id(comuni_id_list[i])
        df.loc[cid, "positivi"] = int(values[i*2])
        df.loc[cid, "positivi_1000"] = round(values[i*2+1], 4) # 4 should suffice

    df["datetime"] = dt
    df["denominazione"] = comuni.loc[df.index]
    return df


giscovid_url = "https://giscovid.sdp.csi.it/tiles/data"

def load_comuni():
    """
    Load a dictionary of id:name values, where `id` 
    is a unique identifier for each municipality in Italy
    (as defined by ISTAT), `name` is the municipality's name

    Arguments:
    none

    Returns:
    comuni: a dictionary -- as described above
    """
    dtypes = {"codice_comune": str, "denominazione": str}
    df = pd.read_csv("comuni_piemonte.csv", delimiter=";", dtype=dtypes)
    return df.set_index("codice_comune")


def fetch_current_datetime():
    """
    Return a datetime object of the latest available update
    (wrapper for _get_datetime without needing to know the
    target url).
    
    When slow polling, it is recommended to use fetch_current_datetime()
    before fetch_current_data() to make sure that the available
    data would be new (fetch_current_datetime() makes only one, 
    lightweight GET request).

    Returns:
    dt: a datetime of the latest update
    """
    dt = _get_datetime(giscovid_url)
    return dt

def fetch_current_data():
    """
    Collect various types of data (latest datetime, list of
    municipalities, list of activate cases) and return a 
    DataFrame with the latest data available

    Returns: a pandas DataFrame, as returned by parse_data()
    """
    dt = _get_datetime(giscovid_url)
    cols = _get_header(giscovid_url)
    data = _get_data(giscovid_url)

    comuni = load_comuni()

    return _parse_data(data, cols, dt, comuni)

def fetch_data_from_files(in_file, va_file, dt):
    """
    Given a path for the in.dat and va.dat files (i.e. the files
    typically downloaded from `giscovid_url`), compute the pandas
    DataFrame with the relevant data (no data is downloaded in this
    function -- useful for previously downloaded data)

    Returns: a pandas DataFrame, as returned by parse_data()
    """
    cols = _load_header(va_file)
    data = _load_data(in_file)

    comuni = load_comuni()

    return _parse_data(data, cols, dt, comuni)

if __name__ == "__main__":
    df = fetch_current_data()
    print(df)
