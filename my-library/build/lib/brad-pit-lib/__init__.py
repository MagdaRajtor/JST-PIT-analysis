from .graph import create_table, create_hist, visualize
from .income import prepare_file, compare_income, double_names, drop_double_names
from .params import param, full_param
from .people import ppl_income_w, ppl_income_p, ppl_income_g

#importowanie, żeby potem przy użyciu można było robić "from brad-pit-lib import full_param"
#zamiast "from brad-pit-lib.params import full_param"
#(chyba)