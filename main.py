import pandas as pd
from pyproj import Transformer
import folium

# --- Step 1: Read CSV ---
data_raw = pd.read_csv("ch.bfe.elektrizitaetsproduktionsanlagen/ElectricityProductionPlant.csv")

# --- Step 2: Filter your data ---
data = data_raw[
    (data_raw["SubCategory"] == "subcat_2") &
    (data_raw["PlantCategory"].isin(["plantcat_8", "plantcat_9", "plantcat_10"])) &
    (data_raw["Canton"] == "BE")
    #(data_raw["PostCode"] == 3510)
].copy()

# --- Step 3: Transform coordinates from EPSG:2056 -> EPSG:4326 ---
transformer = Transformer.from_crs("epsg:2056", "epsg:4326", always_xy=True)
data[["lon", "lat"]] = data.apply(
    lambda row: transformer.transform(row["_x"], row["_y"]), axis=1, result_type="expand"
)

# --- Drop rows with missing coordinates or TotalPower ---
data = data.dropna(subset=["lon", "lat", "TotalPower"])

# --- Step 4: Compute scaling factor for TotalPower ---
power_min = data["TotalPower"].min()
power_max = data["TotalPower"].max()

def scale_radius(power, min_radius=2, max_radius=20):
    """Scale TotalPower to a circle radius between min_radius and max_radius"""
    return min_radius + (power - power_min) / (power_max - power_min) * (max_radius - min_radius)

# --- Step 5: Create folium map ---
center_lat = data["lat"].mean()
center_lon = data["lon"].mean()
m = folium.Map(location=[center_lat, center_lon], zoom_start=12)

# Add proportional circle markers without clustering
for _, row in data.iterrows():
    folium.CircleMarker(
        location=[row["lat"], row["lon"]],
        radius=scale_radius(row["TotalPower"]),
        color='blue',
        fill=True,
        fill_color='blue',
        fill_opacity=0.55,
        stroke=False
    ).add_to(m)

# --- Step 6: Show or save ---
#m  # uncomment if running in Jupyter to display inline
m.save("index.html")  # save as HTML
