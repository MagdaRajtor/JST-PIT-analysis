import pandas as pd

def ppl_income_w(data,file):
    """średni dochód opodatkowany mieszkańca województwa (mean taxable income per województwo resident); 
    data available only for 2020"""
    opod = 0.85 # from GUS data: 85% of society pays taxes (is of working or retirement age)
    mult = 0.016 # 1.6% of PIT tax from a województwo becomes its income
    df = pd.read_excel(file, skiprows=8)
    data["ludność"] = df.iloc[:, 1]
    # d2020: whole PIT from a given JST, divided by the part of residents that pay taxes
    data["d2020"] = (data["2020"]//mult).div((data.ludność*opod), axis=0)
    data["d2020"] = round(data["d2020"], 1)
    return data

def ppl_income_p(data,file):
    """średni dochód opodatkowany mieszkańca powiatu lub miasta na prawach powiatu"""
    opod = 0.85
    mult = 0.1025  # 10.25% of PIT tax from a powiat becomes its income
    df = pd.read_excel(file, skiprows=9, dtype={"Unnamed: 1": str})
    df = df.iloc[:, [1, 2]]
    pom = []
    for ind in data.index:
        code = data["kod"][ind][:4]
        found = df.loc[df["Unnamed: 1"] == code]  # kod terytorialny (territorial code)
        pom.append(found.iloc[0, 1])
    data["ludność"] = pom
    data["d2020"] = (data["2020"] // mult).div((data.ludność * opod), axis=0)
    data["d2020"] = round(data["d2020"], 1)
    return data

def ppl_income_g(data, file, woj):
    """średni dochód opodatkowany mieszkańca gminy"""
    opod = 0.85
    mult = 0.3934
    # gminy are given for a single województwo
    data = data.loc[data["województwo"] == woj]
    if woj == "śląskie":
        woj = "śląske" # fixing an error in original data
    df = pd.read_excel(file, skiprows=7, dtype={"Unnamed: 1": str}, sheet_name=woj.capitalize())
    df = df.iloc[:, [1, 2]]
    df.columns = ["k", "l"]
    df = df[df.k != '       '] # such spaces instead of NaNs used in data
    df["Unnamed: 1"] = df["k"].astype(str).str[:6] # 6-digit instead of 7-digit codes
    pom = []
    for ind in data.index:
        code = data["kod"][ind][:6]
        found = df.loc[df["Unnamed: 1"] == code]
        pom.append(found.iloc[0, 1])
    data["ludność"] = pom
    data["d2020"] = (data["2020"] // mult).div((data.ludność * opod), axis=0)
    data["d2020"] = round(data["d2020"], 1)
    return data
