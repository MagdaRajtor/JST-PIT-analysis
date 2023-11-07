import pandas as pd

def prepare_file(file, year):
    """prepare dataframes from Excel data"""
    # read all data as strings to preserve the zeros in codes (so 0201 instead of 21)
    pom = pd.read_excel(file, skiprows=6, dtype=str)
    pom["kod"] = pom.iloc[:, 0] + pom.iloc[:, 1] + pom.iloc[:, 2]  # create one territorial code
    if year == "2019":
        result = pom.iloc[:, [15, 10]]
        result.columns = ["kod", "2019"]
    elif year == "2020":
        result = pom.iloc[:, [15, 10, 4, 5, 6, ]]
        # use updated names (so powiat karkonoski(jeleniogórski) instead of jeleniogórski)
        result.columns = ["kod", "2020", "nazwa", "województwo", "powiat"]
    result[year] = result[year].astype(float)
    return result


def compare_income(file1, file2):
    """combine income data from both years"""
    df19 = prepare_file(file1, "2019")
    df20 = prepare_file(file2, "2020")
    # use newer (2020) territorial codes
    joined = df19.merge(df20, on="kod", how="right")
    return joined


def double_names(df):
    res = []
    for idx, name in enumerate(df["nazwa"].value_counts().index.tolist()):
        if df["nazwa"].value_counts()[idx] > 1:
            res.append(name)
    return res


def drop_double_names(df, miasto=False):
    """delete all names which were used more than once;
    for data about gminy (e.g. Garwolin once as a gmina wiejska and once as miejska),
    and about miasta na prawach powiatu (both as a powiat and a gmina)"""
    names = double_names(df)
    result = df[df.nazwa.isin(names) == False]
    for name in names:
        pom = df.loc[df["nazwa"] == name]
        d19, d20 = pom.iloc[:,1].sum(), pom.iloc[:,2].sum()  # sum the incomes
        # only the 1st code is taken, since only first 4 digits are needed for further analysis
        new_row = {"kod": pom.iloc[0,0], "2019": d19, "2020": d20, "nazwa": pom.iloc[0,3], \
                   "województwo": pom.iloc[0,4], "powiat": pom.iloc[0,5]}
        result = result.append(new_row, ignore_index=True)
    # a makeshift solution for miasta npp (since they doubled - no such issue for other data files)
    if miasto == True:
        result["2019"] = result["2019"].div(2)
        result["2020"] = result["2020"].div(2)
    return result
