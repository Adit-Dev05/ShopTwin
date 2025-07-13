store_graph = {
    "nodes": {
        # Entrances/Exits
        "entrance_west": {"x": 100, "y": 900},
        "entrance_east": {"x": 1200, "y": 900},
        "exit_main": {"x": 650, "y": 950},
        # Main intersections
        "int_1": {"x": 200, "y": 900},
        "int_2": {"x": 200, "y": 700},
        "int_3": {"x": 650, "y": 700},
        "int_4": {"x": 1100, "y": 700},
        # Section entries
        "toys_entry": {"x": 100, "y": 700},
        "bakery_entry": {"x": 1200, "y": 200},
        "checkout_entry": {"x": 650, "y": 950},
    },
    "edges": [
        ["entrance_west", "int_1"],
        ["int_1", "int_2"],
        ["int_2", "toys_entry"],
        ["int_1", "checkout_entry"],
        ["checkout_entry", "exit_main"],
        ["int_1", "int_3"],
        ["int_3", "int_4"],
        ["int_4", "bakery_entry"],
        ["entrance_east", "int_4"],
    ],
    "section_entries": {
        "Toys": "toys_entry",
        "Bakery": "bakery_entry",
        "Checkout": "checkout_entry",
    }
} 