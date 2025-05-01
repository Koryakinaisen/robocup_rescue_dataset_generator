# data_pipeline/parse_static_objects.py
import json
import xml.etree.ElementTree as ET
from config import STATIC_OBJECTS_JSON


def _strip_ns(tag):
    return tag.split("}", 1)[1] if "}" in tag else tag


def _parse_gml(gml_path, out_json):
    tree = ET.parse(gml_path)
    root = tree.getroot()

    # --- Nodes ---
    nodes = {}
    for node in root.iter():
        if _strip_ns(node.tag) == "Node":
            node_id = next((node.attrib[k] for k in node.attrib if k.endswith("id")), None)
            if not node_id: continue
            coords_el = node.find(".//{*}coordinates")
            if not (coords_el is not None and coords_el.text): continue
            try:
                x, y = map(float, coords_el.text.strip().split(","))
                nodes[node_id] = {"locationX": x, "locationY": y}
            except ValueError:
                pass

    # --- Edges ---
    edges = {}
    for edge in root.iter():
        if _strip_ns(edge.tag) != "Edge": continue
        edge_id = next((edge.attrib[k] for k in edge.attrib if k.endswith("id")), None)
        if not edge_id: continue
        coords = []
        for dnode in edge.findall(".//{*}directedNode"):
            href = next((dnode.attrib[k] for k in dnode.attrib if k.endswith("href")), "")
            ref = href.lstrip("#")
            if ref in nodes: coords.append(nodes[ref])
        edges[edge_id] = coords

    # --- Roads & Buildings ---
    roads, buildings = [], []
    for elem in root.iter():
        tag = _strip_ns(elem.tag)
        if tag not in ("road", "building"): continue
        elem_id = next((elem.attrib[k] for k in elem.attrib if k.endswith("id")), None)
        if not elem_id: continue
        edge_coords = []
        face = elem.find(".//{*}Face")
        if face:
            for dedge in face.findall(".//{*}directedEdge"):
                href = next((dedge.attrib[k] for k in dedge.attrib if k.endswith("href")), "")
                ref = href.lstrip("#")
                if ref in edges: edge_coords.append(edges[ref])
        (roads if tag == "road" else buildings).append(
            {"id": elem_id, "coordinates": edge_coords}
        )

    with open(out_json, "w", encoding="utf-8") as f:
        json.dump({"roads": roads, "buildings": buildings}, f, indent=2, ensure_ascii=False)
    print(f"[static_objects] &rarr; {out_json}")



def generate_static_objects_file(map_path):
   _parse_gml(map_path, STATIC_OBJECTS_JSON)
