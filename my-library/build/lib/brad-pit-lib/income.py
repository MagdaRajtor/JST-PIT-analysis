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
