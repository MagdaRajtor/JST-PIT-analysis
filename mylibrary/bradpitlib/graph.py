import matplotlib.pyplot as plt

def create_table(df):
    fig, ax = plt.subplots()
    fig.patch.set_visible(False)
    ax.axis('off')
    ax.table(cellText=df.values, colLabels=df.columns, loc='center')
    fig.tight_layout()
    plt.show()

def create_hist(df):
    df.plot(kind='bar', color=['indianred', 'steelblue'])
    plt.subplots_adjust(bottom=0.35)
    current_values = plt.gca().get_yticks()
    plt.gca().set_yticklabels(['{:.0f}'.format(x) for x in current_values])  # no e notation
    plt.gca().set_yticklabels(['{:,.0f}'.format(x) for x in current_values])  # add commas to large numbers
    plt.subplots_adjust(left=0.16)
    plt.show()

def visualize(data, col1, col2, woje=None, powi=None, hist=False, all=False, x="nazwa"):
    """this functions compares 2 columns from a dataframe; by default returns a table (optionally a histogram)"""
    # if there is a powiat-województwo conflict, the chosen powiat "wins"
    if powi != None:
        data = data.loc[data["powiat"] == powi]
    elif woje != None:
        data = data.loc[data["województwo"] == woje]
    if hist:
        #  X-axis: names of województwa/powiaty/etc.
        data.set_index(x, inplace=True)
        show_df = data[[col1, col2]]
        create_hist(show_df)
    else:
        if all:
            # shows table with full data, if wanted, by default only 30 first rows
            show_df = data[[x, col1, col2]]
        else:
            show_df = data[[x, col1, col2]]
            show_df = show_df.iloc[:30,:]
        create_table(show_df)
