# Build Map

We provide `mosstool` as a powerful tool to build your own map for the city simulator.

## Install `mosstool`

```bash
pip install mosstool
```

## Generate the `Map` format output

```python
from mosstool.map.osm import RoadNet, Building
from mosstool.map.builder import Builder
from mosstool.util.format_converter import dict2pb
projstr = "+proj=tmerc +lat_0=22.54095 +lon_0=113.90899"
rn = RoadNet(
    proj_str=projstr,
    max_latitude=39.92,
    min_latitude=39.78,
    max_longitude=116.32,
    min_longitude=116.40,
)
roadnet = rn.create_road_net("cache/topo.geojson")
building = Building(
    proj_str=projstr,
    max_latitude=39.92,
    min_latitude=39.78,
    max_longitude=116.32,
    min_longitude=116.40,
)
aois = building.create_building("cache/aois.geojson")
builder = Builder(
    net=roadnet,
    aois=aois,
    proj_str=projstr,
)
pb = dict2pb(m, Map())
with open("data/temp/map.pb", "wb") as f:
    f.write(pb.SerializeToString())
```

- Here `max_latitude`, `min_latitude`, `max_longitude`, `min_longitude` describe the bounding box of the area from which data is to be obtained from OSM, and all are in WGS84 coordinates.
- `proj_str` is a [PROJ.4](https://proj.org/en/9.5/) projection string, used to transform longitude and latitude coordinates into planar xy coordinates. Generally, if there are no special requirements, the `proj_str` can be directly set to a Transverse Mercator projection centered on the map's center, which is `f"+proj=tmerc +lat_0={(max_latitude+min_latitude)/2} +lon_0={(max_longitude+min_longitude)/2}"`. And must remain the same during this process.

:::{caution}
The `proj_str` must be the same in the `RoadNet` and `Building` classes, and the `Builder` class.
:::

**It's worth noting that** the `features` in output GeoJSON file of `create_road_net()` and `create_building()` remains in WGS84 coordinates. The provision of `proj_str` is because using planar xy coordinates is more precise than latitude and longitude coordinates when handling the internal topological relationships of the road network.
