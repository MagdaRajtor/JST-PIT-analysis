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
        data.set_index(x, inplace=True)
        show_df = data[[col1, col2]]
        create_hist(show_df)
    else:
        if all:
            # jeśli wskazane, to pokazuje całość danych w tabeli
            show_df = data[[x, col1, col2]]
        else:
            # domyślnie tylko 30 pierwszych rzędów
            show_df = data[[x, col1, col2]]
            show_df = show_df.iloc[:30,:]
        create_table(show_df)
