import matplotlib.pyplot as plt

def create_table(df):
    fig, ax = plt.subplots()
    fig.patch.set_visible(False) # schować osie
    #ax.axis('tight')
    ax.axis('off')
    ax.table(cellText=df.values, colLabels=df.columns, loc='center')
    fig.tight_layout()
    plt.show()

def create_hist(df):
    df.plot(kind='bar', color=['indianred', 'steelblue'])
    plt.subplots_adjust(bottom=0.35)  # żeby nie ucinało nazw na dole
    current_values = plt.gca().get_yticks()
    plt.gca().set_yticklabels(['{:.0f}'.format(x) for x in current_values])  # bez notacji e
    plt.gca().set_yticklabels(['{:,.0f}'.format(x) for x in current_values])  # przecinki na dużych liczbach
    plt.subplots_adjust(left=0.16)
    plt.show()

def visualize(data, col1, col2, woje=None, powi=None, hist=False, all=False, x="nazwa"):
    """funkcja do zestawienia dwóch kolumn z ramki danych; daje tabelę (domyślnie) lub histogram"""
    # jeśli konflikt powiat-województwo, to wybrany powiat "wygrywa"
    if powi != None:
        data = data.loc[data["powiat"] == powi]
    elif woje != None:
        data = data.loc[data["województwo"] == woje]
    if hist:
        # domyślnie na osi X są nazwy województw/powiatów/itd.
        new_data = data.set_index(x)
        show_df = new_data[[col1, col2]]
        create_hist(show_df)
    else:
        if all:
            # jeśli wskazane, to pokazuje całość danych w tabeli
            show_df = data[[x, col1, col2]]
        else:
            # domyślnie tylko 15 pierwszych rzędów
            show_df = data[[x, col1, col2]]
            show_df = show_df.iloc[:15,:]
        create_table(show_df)




import pandas as pd

def prepare_file(file, year):
    """przygotowanie ramek danych z plików"""
    # wczytujemy jako string, żeby zachować zera (tzn. kod 0201 zamiast 21)
    pom = pd.read_excel(file, skiprows=6, dtype=str)
    # jedna kolumna z kodem terytorialnym
    pom["kod"] = pom.iloc[:, 0] + pom.iloc[:, 1] + pom.iloc[:, 2]
    if year == "2019":
        result = pom.iloc[:, [15, 10]]
        result.columns = ["kod", "2019"]
        #result[year] = result[year].astype(float)
    elif year == "2020":
        result = pom.iloc[:, [15, 10, 4, 5, 6, ]]
        # bierzemy nowsze nazwy (np. powiat karkonoski(jeleniogórski) zamiast jeleniogórski)
        result.columns = ["kod", "2020", "nazwa", "województwo", "powiat"]
    # do wykresów potrzebne nam jako liczby (float, a nie int bo przy miastach_npp int było za mało)
    result[year] = result[year].astype(float)
    return result


def compare_income(file1, file2):
    """połączenie danych o dochodach z PIT z dwóch lat"""
    df19 = prepare_file(file1, "2019")
    df20 = prepare_file(file2, "2020")
    # posługujemy się nowszymi (2020) kodami terytorialnymi
    joined = df19.merge(df20, on="kod", how="right")
    return joined




def double_names(df):
    """zwraca listę nazw pojawiających się w df więcej niż raz (niepożądane)"""
    res = []
    for idx, name in enumerate(df["nazwa"].value_counts().index.tolist()):
        if df["nazwa"].value_counts()[idx] > 1:
            res.append(name)
    return res

def drop_double_names(df, miasto=False):
    """funkcja do likwidacji zdublowanych (lub więcej) nazw - do plików z danymi o gminach
    (np. Garwolin raz jako gmina wiejska a raz jako miejska) oraz do miast na prawach powiatu (jako powiat i gmina)"""
    names = double_names(df)
    # na razie wyrzucamy wiersze z powtarzającymi się nazwami
    result = df[df.nazwa.isin(names) == False]
    for name in names:
        pom = df.loc[df["nazwa"] == name]
        # sumujemy dochody
        d19, d20 = pom.iloc[:,1].sum(), pom.iloc[:,2].sum()
        # bierzemy 1-szy kod, bo różnią się dwoma ostatnimi cyframi - co w dalszej analizie i tak jest bez znaczenia
        new_row = {"kod": pom.iloc[0,0], "2019": d19, "2020": d20, "nazwa": pom.iloc[0,3], \
                   "województwo": pom.iloc[0,4], "powiat": pom.iloc[0,5]}
        # dodajemy "scalony" wiersz
        result = result.append(new_row, ignore_index=True)
    # przy wczytywaniu miasta npp się dublowały (więc policzone dochody też) - reszta plików ok i nie wiem w czym problem
    # zatem nieidealne rozwiązanie w postaci:
    if miasto == True:
        result["2019"] = result["2019"].div(2)
        result["2020"] = result["2020"].div(2)
    return result



import pandas as pd

def param(type, w_file, p_file, w_name, p_name=None, g_file=None):
    """type='var' policzy wariancję, a 'mean' średnią; funkcja dla pojedycznego województwa lub powiatu + województwa"""
    row = {}
    if p_name is None:
        # trzymamy dane jednostki nadrzędnej
        upper = w_file.loc[w_file["nazwa"] == w_name]
        code = upper.iloc[0, 0][:2] # 2 pierwsze cyfry mają znaczenie
        pom = p_file.loc[p_file["województwo"] == w_name]
        df = pom[pom["kod"].str.match(code)]
    else:
        # tutaj i powiat i województwo, bo nazwy powiatów się powtarzają (np. tomaszowski)
        upper = p_file.loc[(p_file["nazwa"] == p_name) & (p_file["województwo"] == w_name)]
        code = upper.iloc[0, 0][:4] # 4 pierwsze cyfry mają znaczenie
        pom = g_file.loc[g_file["powiat"] == p_name]
        df = pom[pom["kod"].str.match(code)]
    if type == "var":
        result = df[["2019", "2020"]].var()
        row = {"kod": code, "nazwa": upper.iloc[0,3], "v2019": result[0], "v2020": result[1]}
    elif type == "mean":
        result = df[["2019", "2020"]].mean()
        # od razu z dochodami dla całej JST dla obu lat
        row = {"kod": code, "nazwa": upper.iloc[0,3], "m2019": result[0], "m2020": result[1], \
               "2019": upper.iloc[0,1], "2020": upper.iloc[0,2]}
    return row


def full_param(type, w_file, p_file, g_file=None, powiat=False):
    """dla wszystkich województw lub powiatów"""
    result = pd.DataFrame()
    names = w_file["nazwa"].tolist()
    ex_names = [None] * w_file.shape[0]
    if powiat:
        names = p_file["województwo"].tolist()
        ex_names = p_file["nazwa"].tolist()
    for name, ex_name in zip(names, ex_names):
        new_row = param(type, w_file, p_file, name, ex_name, g_file)
        result = result.append(new_row, ignore_index=True)
    return result



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
        pom.append(found.iloc[0, 2])
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
        pom.append(found.iloc[0, 2])
    data["ludność"] = pom
    data["d2020"] = (data["2020"] // mult).div((data.ludność * opod), axis=0)
    data["d2020"] = round(data["d2020"], 1)
    return data
