"""
===============================================================
FastBox Mystery Delivery System — logistics simulator
===============================================================

Assignment: Python Assignment 2026
Author:     (Your Name)

Description:
    Simulates one day of FastBox delivery operations.
    Reads a JSON input file, assigns packages to the nearest
    delivery agent, simulates the deliveries (with optional
    random delays), and writes a detailed report to report.json.

Usage:
    py delivery_system.py [input_file] [output_file]

    Defaults:
        input_file  -> data.json
        output_file -> report.json

Bonus features included:
    1. Random delivery delays (0-30 minutes per package)
    2. ASCII route map visualisation
    3. New agent joining mid-day (after 50% of packages assigned)
    4. Export top performer to top_performer.csv
===============================================================
"""

import json
import math
import random
import csv
import sys
import os
from typing import Dict, List, Tuple, Any


# =====================================================
# Section 1 - Distance Utility
# =====================================================

def euclidean_distance(point_a, point_b):
    """
    Calculate the straight-line (Euclidean) distance between two 2-D points.
    Formula: d = sqrt((x2 - x1)^2 + (y2 - y1)^2)
    """
    dx = point_b[0] - point_a[0]
    dy = point_b[1] - point_a[1]
    return round(math.sqrt(dx ** 2 + dy ** 2), 4)


# =====================================================
# Section 2 - JSON Parsing
# =====================================================

def load_input(filepath):
    """
    Read and parse the input JSON file.
    Supports both dict format: {"W1": [x,y]} and
    list format: [{"id": "W1", "location": [x,y]}]
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Input file not found: {filepath}")

    with open(filepath, "r") as f:
        data = json.load(f)

    # Validate required top-level keys
    required_keys = {"warehouses", "agents", "packages"}
    missing = required_keys - data.keys()
    if missing:
        raise ValueError(f"Input JSON is missing required keys: {missing}")

    # Normalise warehouses if they are in list format
    if isinstance(data["warehouses"], list):
        data["warehouses"] = {
            w.get("id", w.get("warehouse_id")): w["location"]
            for w in data["warehouses"]
        }

    # Normalise agents if they are in list format
    if isinstance(data["agents"], list):
        data["agents"] = {
            a["id"]: a["location"]
            for a in data["agents"]
        }

    # Normalise packages: unify key names (warehouse vs warehouse_id)
    normalised_packages = []
    for pkg in data["packages"]:
        normalised_packages.append({
            "id":          pkg["id"],
            "warehouse":   pkg.get("warehouse") or pkg.get("warehouse_id"),
            "destination": pkg["destination"],
        })
    data["packages"] = normalised_packages

    print(f"[OK] Loaded '{filepath}'")
    print(f"     Warehouses : {len(data['warehouses'])}")
    print(f"     Agents     : {len(data['agents'])}")
    print(f"     Packages   : {len(data['packages'])}")

    return data


# =====================================================
# Section 3 - Package Assignment (nearest agent)
# =====================================================

def assign_packages(warehouses, agents, packages):
    """
    Assign each package to the nearest available agent.

    'Nearest' = the agent whose current position is closest
    (Euclidean) to the package's originating warehouse.

    Tie-breaking: if two agents are equidistant, the agent
    whose ID comes first alphabetically is preferred.
    """
    # Initialise empty lists for every agent
    assignments = {aid: [] for aid in agents}

    for pkg in packages:
        warehouse_loc = warehouses[pkg["warehouse"]]

        # Find nearest agent (sort alphabetically for tie-breaking)
        nearest_agent = None
        min_distance  = float("inf")

        for agent_id in sorted(agents.keys()):
            dist = euclidean_distance(agents[agent_id], warehouse_loc)
            if dist < min_distance:
                min_distance  = dist
                nearest_agent = agent_id

        assignments[nearest_agent].append(pkg)
        print(f"    Package {pkg['id']} (warehouse {pkg['warehouse']}) "
              f"-> Agent {nearest_agent}  [dist={min_distance:.2f}]")

    return assignments


# =====================================================
# Section 4 - Simulation (deliveries + distance)
# =====================================================

def simulate_deliveries(assignments, warehouses, agents, enable_delays=True):
    """
    Simulate each agent picking up and delivering packages.

    Delivery model (sequential per agent):
        1. Agent travels from current position -> warehouse.
        2. Agent travels from warehouse -> package destination.
        3. Agent position updates to destination.

    Efficiency = total_distance / packages_delivered  (lower = better)
    """
    results = {}
    current_positions = {aid: list(loc) for aid, loc in agents.items()}

    for agent_id, packages in assignments.items():
        agent_pos   = current_positions[agent_id]
        total_dist  = 0.0
        total_delay = 0
        deliveries  = []

        for pkg in packages:
            warehouse_loc = warehouses[pkg["warehouse"]]
            destination   = pkg["destination"]

            # Leg 1: agent position -> warehouse
            leg1 = euclidean_distance(agent_pos, warehouse_loc)
            # Leg 2: warehouse -> destination
            leg2 = euclidean_distance(warehouse_loc, destination)
            pkg_distance = round(leg1 + leg2, 4)
            total_dist   = round(total_dist + pkg_distance, 4)

            # Bonus Feature 1: random delivery delay
            delay = random.randint(0, 30) if enable_delays else 0
            total_delay += delay

            deliveries.append({
                "package_id":       pkg["id"],
                "warehouse":        pkg["warehouse"],
                "leg1_to_wh":       round(leg1, 2),
                "leg2_to_dest":     round(leg2, 2),
                "package_distance": round(pkg_distance, 2),
                "delay_min":        delay,
            })

            # Update agent position to delivery destination
            agent_pos = list(destination)

        pkg_count  = len(packages)
        efficiency = round(total_dist / pkg_count, 2) if pkg_count > 0 else 0.0

        agent_result = {
            "packages_delivered": pkg_count,
            "total_distance":     round(total_dist, 2),
            "efficiency":         efficiency,
            "deliveries":         deliveries,
        }
        if enable_delays:
            agent_result["total_delay_min"] = total_delay

        results[agent_id] = agent_result

    return results


# =====================================================
# Section 5 - Report Generation
# =====================================================

def generate_report(simulation_results):
    """
    Build the final report dictionary.

    best_agent = agent with the lowest efficiency score
    (lowest avg distance per package = most efficient).
    """
    report = {}

    active_agents = {
        aid: data
        for aid, data in simulation_results.items()
        if data["packages_delivered"] > 0
    }

    for agent_id, data in simulation_results.items():
        report[agent_id] = {
            "packages_delivered": data["packages_delivered"],
            "total_distance":     data["total_distance"],
            "efficiency":         data["efficiency"],
        }

    if active_agents:
        best_agent = min(
            active_agents,
            key=lambda aid: (active_agents[aid]["efficiency"], aid),
        )
    else:
        best_agent = None

    report["best_agent"] = best_agent
    return report


# =====================================================
# Bonus Feature 2 - ASCII Route Visualiser
# =====================================================

def ascii_route_map(warehouses, agents, packages, grid_size=30):
    """Print an ASCII grid showing warehouses, agents, and destinations."""
    print("\n" + "=" * 52)
    print("  ASCII ROUTE MAP")
    print("=" * 52)

    all_coords = (
        list(warehouses.values())
        + list(agents.values())
        + [pkg["destination"] for pkg in packages]
    )
    xs = [c[0] for c in all_coords]
    ys = [c[1] for c in all_coords]
    x_min, x_max = min(xs), max(xs)
    y_min, y_max = min(ys), max(ys)
    x_range = max(x_max - x_min, 1)
    y_range = max(y_max - y_min, 1)

    def to_grid(x, y):
        col = int((x - x_min) / x_range * (grid_size - 1))
        row = int((y - y_min) / y_range * (grid_size - 1))
        return col, (grid_size - 1) - row  # invert y-axis

    grid = [["." for _ in range(grid_size)] for _ in range(grid_size)]

    for loc in warehouses.values():
        c, r = to_grid(*loc)
        grid[r][c] = "W"

    for pkg in packages:
        c, r = to_grid(*pkg["destination"])
        if grid[r][c] == ".":
            grid[r][c] = "D"

    for loc in agents.values():
        c, r = to_grid(*loc)
        if grid[r][c] == ".":
            grid[r][c] = "A"

    for row in grid:
        print("  " + " ".join(row))

    print("\n  Legend: W=Warehouse  A=Agent  D=Destination  .=Empty")
    print("=" * 52 + "\n")


# =====================================================
# Bonus Feature 3 - New Agent Joining Mid-Day
# =====================================================

def add_midday_agent(agents, assignments, packages, warehouses, join_fraction=0.5):
    """
    A new agent (A_NEW) joins after 50% of packages have been assigned.
    A_NEW is placed at the centroid of all warehouse locations and
    takes over all packages from the midpoint onward.
    """
    total_packages = len(packages)
    join_at_index  = int(total_packages * join_fraction)

    if join_at_index >= total_packages:
        print("[!] A_NEW has no packages to deliver — skipping.")
        return agents, assignments

    # Centroid of all warehouses
    all_locs  = list(warehouses.values())
    cx = sum(loc[0] for loc in all_locs) / len(all_locs)
    cy = sum(loc[1] for loc in all_locs) / len(all_locs)

    new_id = "A_NEW"
    agents[new_id]     = [cx, cy]
    assignments[new_id] = []

    packages_for_new = packages[join_at_index:]
    reassign_ids     = {p["id"] for p in packages_for_new}

    print(f"\n[BONUS] Agent {new_id} joins mid-day at ({cx:.1f}, {cy:.1f})")
    print(f"        Taking over {len(packages_for_new)} packages "
          f"(package #{join_at_index + 1} onward)")

    # Remove those packages from whoever had them
    for aid in list(assignments.keys()):
        if aid == new_id:
            continue
        assignments[aid] = [p for p in assignments[aid] if p["id"] not in reassign_ids]

    assignments[new_id] = packages_for_new
    return agents, assignments


# =====================================================
# Bonus Feature 4 - Export Top Performer CSV
# =====================================================

def export_top_performer_csv(report, simulation_results, output_path):
    """Write the best agent stats to a CSV file."""
    best = report.get("best_agent")
    if not best:
        print("[!] No best agent — skipping CSV export.")
        return

    data = simulation_results[best]
    fieldnames = ["agent_id", "packages_delivered", "total_distance", "efficiency"]
    if "total_delay_min" in data:
        fieldnames.append("total_delay_min")

    row = {
        "agent_id":           best,
        "packages_delivered": data["packages_delivered"],
        "total_distance":     data["total_distance"],
        "efficiency":         data["efficiency"],
    }
    if "total_delay_min" in data:
        row["total_delay_min"] = data["total_delay_min"]

    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow(row)

    print(f"[BONUS] Top performer exported -> '{output_path}'")


# =====================================================
# Section 6 - Save Output
# =====================================================

def save_report(report, output_path):
    """Serialise the final report to a JSON file."""
    with open(output_path, "w") as f:
        json.dump(report, f, indent=4)
    print(f"\n[OK] Report saved -> '{output_path}'")


# =====================================================
# Section 7 - Console Summary
# =====================================================

def print_summary(report, simulation_results):
    """Print a formatted delivery summary table."""
    print("\n" + "=" * 62)
    print("  FASTBOX DELIVERY REPORT SUMMARY")
    print("=" * 62)
    print(f"  {'Agent':<10} {'Packages':>10} {'Distance':>12} {'Efficiency':>12}")
    print("  " + "-" * 50)

    for key, val in report.items():
        if key == "best_agent":
            continue
        star = " BEST" if key == report["best_agent"] else ""
        delay = ""
        if "total_delay_min" in simulation_results.get(key, {}):
            delay = f" (+{simulation_results[key]['total_delay_min']}min delay)"
        print(
            f"  {key:<10} {val['packages_delivered']:>10} "
            f"{val['total_distance']:>12.2f} {val['efficiency']:>12.2f}"
            f"{star}{delay}"
        )

    print("  " + "-" * 50)
    print(f"\n  Best Agent (most efficient): {report['best_agent']}")
    print("=" * 62 + "\n")


# =====================================================
# Section 8 - Main Entry Point
# =====================================================

def run(input_file="data.json", output_file="report.json", enable_bonus=True):
    """Full pipeline: load -> assign -> simulate -> report -> save."""
    random.seed(42)  # fixed seed for reproducible delays

    print("\n" + "=" * 62)
    print("  FASTBOX DELIVERY SYSTEM - starting simulation ...")
    print("=" * 62)

    # Step 1: Load input
    data       = load_input(input_file)
    warehouses = data["warehouses"]
    agents     = data["agents"]
    packages   = data["packages"]

    # Step 2: Assign packages to nearest agents
    print("\n[->] Assigning packages to nearest agents ...")
    assignments = assign_packages(warehouses, agents, packages)

    # Bonus 3: New agent joins mid-day
    if enable_bonus:
        agents, assignments = add_midday_agent(
            agents, assignments, packages, warehouses
        )

    # Bonus 2: ASCII map
    if enable_bonus:
        ascii_route_map(warehouses, agents, packages)

    # Step 3: Simulate deliveries
    print("[->] Simulating deliveries ...")
    sim_results = simulate_deliveries(
        assignments, warehouses, agents, enable_delays=enable_bonus
    )

    # Step 4: Generate report
    print("[->] Generating report ...")
    report = generate_report(sim_results)

    # Step 5: Save report.json
    save_report(report, output_file)

    # Print summary
    print_summary(report, sim_results)

    # Bonus 4: CSV export
    if enable_bonus:
        csv_path = output_file.replace(".json", "_top_performer.csv")
        export_top_performer_csv(report, sim_results, csv_path)

    # Validation: all packages accounted for
    total = sum(v["packages_delivered"] for v in sim_results.values())
    assert total == len(packages), (
        f"Mismatch! Input={len(packages)} packages, delivered={total}"
    )
    print(f"[OK] Validation passed - all {total} packages delivered.\n")

    return report


if __name__ == "__main__":
    input_file  = sys.argv[1] if len(sys.argv) > 1 else "data.json"
    output_file = sys.argv[2] if len(sys.argv) > 2 else "report.json"
    run(input_file, output_file, enable_bonus=True)
