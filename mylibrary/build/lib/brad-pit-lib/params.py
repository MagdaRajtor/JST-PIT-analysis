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
