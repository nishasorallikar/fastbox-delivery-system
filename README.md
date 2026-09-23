# FastBox Delivery System
### A Logistics Simulation Built in Python
**Technical Assignment · 2026**

---

![Cover](FastBox%20Delivery%20System/FastBox%20Delivery%20System.png)

---

## 📋 What We Had to Build

The assignment gives us a JSON input file with **3 entities**:

| # | Entity | Description |
|---|--------|-------------|
| 01 | **Warehouses** | Fixed points on a 2D coordinate grid |
| 02 | **Agents** | Delivery workers, each with a starting location |
| 03 | **Packages** | Stored at a warehouse, must reach a destination |

**Objective Pipeline:**

`Assign Packages` → `Simulate Deliveries` → `Calculate Distances` → `Generate Report`

![Problem Overview](FastBox%20Delivery%20System/Problem%20Overview.png)

---

## 🗂️ Input%20Format%20%E2%80%94%20JSON

The input file has three top-level keys. The code supports **both** dict format (test cases) and list format (base_case):

```json
{
    "warehouses": { "W1": [34, 29], "W2": [95, 4] },
    "agents":     { "A1": [89, 16], "A2": [52, 21] },
    "packages": [
        { "id": "P1", "warehouse": "W1", "destination": [12, 7] }
    ]
}
```

| Key | Contains | Structure |
|-----|----------|-----------|
| `warehouses` | Locations on grid | `{ id: [x, y] }` |
| `agents` | Delivery workers | `{ id: [x, y] }` |
| `packages` | Items to deliver | `{ warehouse, destination }` |

![Input Format](FastBox%20Delivery%20System/Input%20Format%20%E2%80%94%20JSON.png)

---

## 🧠 Core Algorithm — Step by Step

Six sequential steps form the full pipeline:

| Step | Name | What it does |
|------|------|-------------|
| 01 | **LOAD** | Parse & normalise the JSON input |
| 02 | **CALCULATE** | Compute Euclidean distances |
| 03 | **ASSIGN** | Match each package to the nearest agent |
| 04 | **SIMULATE** | Walk each agent through their deliveries |
| 05 | **REPORT** | Aggregate stats, find best agent |
| 06 | **SAVE** | Write `report.json` to disk |

![Core Algorithm Flow](FastBox%20Delivery%20System/Core%20Algorithm%20Flow.png)

---

## 📐 Euclidean Distance — The Core Formula

Every distance calculation in the system uses one formula:

```
d = √( (x₂ - x₁)² + (y₂ - y₁)² )
```

**Python implementation:**

```python
def euclidean_distance(point_a, point_b):
    dx = point_b[0] - point_a[0]
    dy = point_b[1] - point_a[1]
    return round(math.sqrt(dx ** 2 + dy ** 2), 4)
```

> **Example:** Distance from `[0, 0]` to `[3, 4]` = `√(9 + 16)` = **5.0**
>
> Two points (P₁, P₂) on a 2D grid are connected by the straight-line distance `d`.

![Euclidean Distance](FastBox%20Delivery%20System/Euclidean%20Distance.png)

---

## 📦 Assigning Packages to the Nearest Agent

**Function:** `assign_packages(warehouses, agents, packages)`

For every package, the algorithm:

1. Finds the package's warehouse location
2. Measures distance from **every agent** to that warehouse
3. Assigns the package to the **closest agent**
4. **Tie-breaking:** if two agents are equal distance, alphabetically first wins (A1 before A2)

**Worked example — Package at Warehouse W5:**

```
A1  →  W5  =  8.4   (not nearest)
A2  →  W5  =  6.1   (not nearest)
A3  →  W5  =  9.0   (not nearest)
A4  →  W5  =  4.7   ← NEAREST → Package assigned to A4
```

![Assigning Packages](FastBox%20Delivery%20System/Assigning%20Packages.png)

> **Note:** Agent positions used here are their **starting locations**. Positions only update *during* simulation.

---

## 🚚 Simulating the Delivery Journey

**Function:** `simulate_deliveries(assignments, warehouses, agents)`

Each agent delivers packages **one by one**, updating position after each drop-off:

```
START POSITION  ──[Leg 1]──►  WAREHOUSE  ──[Leg 2]──►  DESTINATION
                                                              ↓
                                                   Agent moves here next
```

**Key formulas:**

```python
package_distance = leg1 + leg2                        # one package
total_distance   = sum of all package_distances       # whole day
efficiency       = total_distance / packages_delivered # lower = better
```

> **Agent position updates after each delivery** — the next package's leg1 starts from the previous destination.

![Simulating the Journey](FastBox%20Delivery%20System/Simulating%20the%20Journey.png)

---

## 📊 Generated Report — report.json

**Function:** `generate_report(simulation_results)`

The output JSON contains stats for every agent plus `best_agent`:

```json
{
    "A1": {
        "packages_delivered": 3,
        "total_distance": 48.56,
        "efficiency": 16.19
    },
    "A2": {
        "packages_delivered": 0,
        "total_distance": 0.0,
        "efficiency": 0.0
    },
    "best_agent": "A1"
}
```

**Best Agent** = agent with the **lowest efficiency score**
(least average distance per package delivered)

![Generated Report](FastBox%20Delivery%20System/Generated%20Report.png)

---

## ⭐ Bonus Features Implemented

All 4 bonus features are built into `delivery_system.py` and activated by default:

| # | Feature | Detail |
|---|---------|--------|
| 01 | **Random Delays** | 0–30 min per package; `random.seed(42)` for reproducibility |
| 02 | **ASCII Route Map** | Terminal grid with `W`/`A`/`D` symbols; Y-axis inverted |
| 03 | **New Agent Mid-Day** | `A_NEW` joins at warehouse centroid after 50% of packages |
| 04 | **CSV Export** | Top performer saved to `report_top_performer.csv` |

![Bonus Features](FastBox%20Delivery%20System/Bonus%20Features.png)

---

## 🗺️ ASCII Route Map — Live Terminal Output

**Function:** `ascii_route_map(warehouses, agents, packages)`

Prints a normalised 30×30 grid to the terminal after assignment:

```
. . . . W . . . . . . . . . . . . . . .
. . . . . . . A . . . . . . . . . . . .
. . . . . . . . . . D . . . . . . . . .
. . . . . . . . . . . . . . . W . . . .
. . . A . . . D . . . . . . . . . . . .
```

**Legend:** `W` = Warehouse &nbsp;|&nbsp; `A` = Agent &nbsp;|&nbsp; `D` = Destination

> All real coordinates are normalised to the grid.
> Y-axis is **inverted** so the map reads correctly top-to-bottom.

![ASCII Route Map](FastBox%20Delivery%20System/ASCII%20Route%20Map.png)

---

## ✅ Test Results — All 11 Cases Passed

The system was validated against all provided test cases:

| Test Case | Packages | Agents | Result |
|-----------|:--------:|:------:|:------:|
| base_case | 5 | 3 | ✅ PASS |
| TC 1 | 12 | 4 | ✅ PASS |
| TC 2 | 10 | 3 | ✅ PASS |
| TC 3 | 6 | 4 | ✅ PASS |
| TC 4 | 12 | 5 | ✅ PASS |
| TC 5 | 10 | 5 | ✅ PASS |
| TC 6 | 9 | 4 | ✅ PASS |
| TC 7 | 10 | 4 | ✅ PASS |
| TC 8 | 11 | 4 | ✅ PASS |
| TC 9 | 8 | 4 | ✅ PASS |
| TC 10 | 11 | 4 | ✅ PASS |

**Validation assertion run on every case:**
```python
assert total_delivered == len(packages)   # Zero packages lost.
```

![Test Results](FastBox%20Delivery%20System/Test%20Results.png)

---

## 🏁 Summary

**Built to be clear, flexible, and verifiable.**

| | |
|--|--|
| 🐍 **Pure Python** | No external libraries — only `json`, `math`, `random`, `csv` |
| 📦 **Flexible** | Handles any number of warehouses, agents, and packages |
| ⭐ **Complete** | 4 bonus features implemented on top of all core requirements |

**How to run:**
```powershell
# Default run (data.json → report.json)
py delivery_system.py

# Custom input/output
py delivery_system.py "test_case_1.json" my_report.json
```

![Summary](FastBox%20Delivery%20System/Summary.png)

---

*FastBox Delivery System — Python Assignment 2026*
