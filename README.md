points json format:

[name]: [x, y, z]
ex. "A": [-1.0, -1.0, -1.0]

faces json format:
    "faces": {
        "F0": {
            "vertices": ["A", "B", "D", "C"],
            "connections": {
            }
        }
    }

Hotkeys:
Q: Select edges
V: Select a point along a selected edge
X: Make a crease between two selected points
W: Select a face
F: Fold selected face