import pandas as pd

def ppl_income_w(data,file):
    """średni dochód opodatkowany mieszkańca województwa; jedynie za 2020 rok, bo tylko takie dane dotyczące ludności"""
    opod = 0.85 # z danych GUS, 85% społeczeństwa jest w wieku po- i produkcyjnym (płaci podatki)
    mult = 0.016 # 1.6% podatku PIT zebranego w województwie trafia do niego jako dochód
    df = pd.read_excel(file, skiprows=8)
    data["ludność"] = df.iloc[:, 1]
    # d2020: cała kwota z podatku PIT zebranego z danej JST podzielona przez część społeczeństwa, która płaci podatki
    data["d2020"] = (data["2020"]//mult).div((data.ludność*opod), axis=0)
    data["d2020"] = round(data["d2020"], 1)
    return data

def ppl_income_p(data,file):
    """średni dochód opodatkowany mieszkańca powiatu lub miasta na prawach powiatu"""
    opod = 0.85
    mult = 0.1025  # 10.25% podatku PIT zebranego w powiecie trafia do niego jako dochód
    df = pd.read_excel(file, skiprows=9, dtype={"Unnamed: 1": str})  # znów żeby zachować zera w kodach
    df = df.iloc[:, [1, 2]]
    pom = []
    for ind in data.index:
        code = data["kod"][ind][:4]
        found = df.loc[df["Unnamed: 1"] == code]  # wiersz z danym kodem terytorialnym
        pom.append(found.iloc[0, 1])
    data["ludność"] = pom
    data["d2020"] = (data["2020"] // mult).div((data.ludność * opod), axis=0)
    data["d2020"] = round(data["d2020"], 1)
    return data

def ppl_income_g(data, file, woj):
    """średni dochód opodatkowany mieszkańca gminy"""
    opod = 0.85
    mult = 0.3934
    # przekazujemy gminy tylko dla 1 województwa
    data = data.loc[data["województwo"] == woj]
    if woj == "śląskie":
        woj = "śląske" # taki błąd w Excelu
    df = pd.read_excel(file, skiprows=7, dtype={"Unnamed: 1": str}, sheet_name=woj.capitalize())
    df = df.iloc[:, [1, 2]]
    df.columns = ["k", "l"]
    df = df[df.k != '       '] # nie było NaN a właśnie takie spacje, więc do usunięcia
    df["Unnamed: 1"] = df["k"].astype(str).str[:6] # kody 6-cyfrowe zamiast 7
    #dalej analogicznie jak przy powiatach:
    pom = []
    for ind in data.index:
        code = data["kod"][ind][:6]
        found = df.loc[df["Unnamed: 1"] == code]
        pom.append(found.iloc[0, 1])
    data["ludność"] = pom
    data["d2020"] = (data["2020"] // mult).div((data.ludność * opod), axis=0)
    data["d2020"] = round(data["d2020"], 1)
    return data
