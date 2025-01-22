__all__ = ["wrap_feature_collection"]


def wrap_feature_collection(features: list[dict], name: str):
    """
    将 GeoJSON Feature 集合包装为 FeatureCollection
    Wrap GeoJSON Feature collection as FeatureCollection

    - **Args**:
    - features: GeoJSON Feature 集合。GeoJSON Feature collection.
    - name: FeatureCollection 名称。FeatureCollection name.

    - **Returns**:
    - dict: GeoJSON FeatureCollection
    """
    return {
        "type": "FeatureCollection",
        "name": name,
        "crs": {
            "type": "name",
            "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"},
        },
        "features": features,
    }
