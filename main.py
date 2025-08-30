import pandas as pd
from pyproj import Transformer
import folium
import matplotlib.pyplot as plt

from bokeh.plotting import figure
from bokeh.resources import CDN
from bokeh.embed import file_html


def get_zips(data: pd.DataFrame, zips: list[int]) -> list[pd.DataFrame]:
    zip_list = []
    for i in zips:
        zip_list.append(data[data_raw["PostCode"] == i])

    return zip_list

data_raw = pd.read_csv("ch.bfe.elektrizitaetsproduktionsanlagen/ElectricityProductionPlant.csv")


data = data_raw[
    (data_raw["SubCategory"] == "subcat_2") &
    (data_raw["PlantCategory"].isin(["plantcat_8", "plantcat_9", "plantcat_10"]))
].copy()


transformer = Transformer.from_crs("epsg:2056", "epsg:4326", always_xy=True)
data[["lon", "lat"]] = data.apply(
    lambda row: transformer.transform(row["_x"], row["_y"]), axis=1, result_type="expand"
)

data["BeginningOfOperation"] = pd.to_datetime(data["BeginningOfOperation"], format="%Y-%m-%d")
data = data.sort_values(by="BeginningOfOperation")
data["cumsum"] = data["TotalPower"].cumsum()
data.to_csv("out.csv")

#plt.step(data["BeginningOfOperation"], data["cumsum"], where="post")
#plt.show()

plot = figure(
    sizing_mode="stretch_both"
)
plot.step(data["BeginningOfOperation"], data["cumsum"])

html = file_html(plot, CDN, "my plot")

with open("export.html", "w") as f:
    f.write(html)