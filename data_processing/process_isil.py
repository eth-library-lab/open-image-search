import re

def find_isil_in_string(in_str:str) -> str:
    """
    finds the isil identifier inside the input str
    two examples are: CH-000511-9 and CH-000008-6
    ISIL identifier number is based on ISO 15511:2019
    this pattern is matched using regex
    """

    ptrn=r"[A-Za-z]{2}-[0-9]{6}-\d{1,2}"
    res = re.search(ptrn, in_str)
    out_str=None
    if res:
        out_str = res[0]

    return out_str


def process_isil_series(ser:pd.Series):
    """
    return a series containing only the isil id contained in the series 
    """
    ser = ser.apply(find_isil_in_string)
    return ser