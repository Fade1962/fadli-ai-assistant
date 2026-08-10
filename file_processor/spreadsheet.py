import pandas as pd


def read_excel(path):

    if path.endswith(".csv"):

        df = pd.read_csv(path)

    else:

        df = pd.read_excel(path)


    return df.to_string()[:12000]
