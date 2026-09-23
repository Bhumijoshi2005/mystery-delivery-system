"""
FastBox Delivery System
-----------------------
My program does the following:
1. reads data from a JSON file
2. gives each package to the nearest agent
3. simulates the route of each agent
4. calculates total distance and efficiency
5. saves the final report to report.json

How to run:
    python delivery_system.py data.json report.json
    If you don't specify report.json, it will default to that filename.
"""

import json
import math
import random
import sys


def normalize_locations(raw):
    """
    Convert location data into this format:
    {"W1": (x, y), "W2": (x, y)}
    """
    if isinstance(raw, dict):
        return {key: tuple(value) for key, value in raw.items()}

    if isinstance(raw, list):
        return {item["id"]: tuple(item["location"]) for item in raw}

    raise ValueError("This format is not supported.")


def normalize_packages(raw):
    """
    Make every package look the same:
    {
        "id": "P1",
        "warehouse": "W1",
        "destination": (x, y)
    }
    """
    packages = []

    for pkg in raw:
        warehouse_key = pkg.get("warehouse", pkg.get("warehouse_id"))
        packages.append({
            "id": pkg["id"],
            "warehouse": warehouse_key,
            "destination": tuple(pkg["destination"]),
        })

    return packages

def load_data(path):
    """Read the file and return clean warehouses, agents, and packages."""
    # Read the JSON file first.
    with open(path, "r") as file:
        raw = json.load(file)

    # Get the data needed for the delivery calculation.
    raw_warehouses = raw["warehouses"]
    raw_agents = raw["agents"]
    raw_packages = raw["packages"]

    # Convert warehouse and agent locations to the same format.
    warehouses = normalize_locations(raw_warehouses)
    agents = normalize_locations(raw_agents)

    # Make the package fields consistent before using them.
    packages = normalize_packages(raw_packages)
    return warehouses, agents, packages

def euclidean_distance(point1, point2):
    """Return the straight-line distance between two points."""
    x1, y1 = point1
    x2, y2 = point2

    # Use the Euclidean formula for the two coordinate pairs.
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

def assign_packages_to_agents(warehouses, agents, packages):
    """Return a dictionary like: {agent_id: [packages]}"""
    assignments = {agent_id: [] for agent_id in agents}

    # Store the nearest agent for a warehouse after finding it once.
    nearest_agent_for_warehouse = {}

    for pkg in packages:
        warehouse_id = pkg["warehouse"]

        if warehouse_id not in nearest_agent_for_warehouse:
            warehouse_location = warehouses[warehouse_id]
            # Compare every agent with this warehouse and choose the closest one.
            nearest_agent_id = min(
                agents,
                key=lambda agent_id: euclidean_distance(agents[agent_id], warehouse_location)
            )
            nearest_agent_for_warehouse[warehouse_id] = nearest_agent_id

        assigned_agent_id = nearest_agent_for_warehouse[warehouse_id]
        assignments[assigned_agent_id].append(pkg)

    return assignments

def simulate_deliveries(warehouses, agents, assignments):
    """Return each agent's delivery summary."""
    report = {}

    for agent_id, agent_packages in assignments.items():
        current_location = agents[agent_id]
        total_distance = 0.0

        for pkg in agent_packages:
            warehouse_location = warehouses[pkg["warehouse"]]
            destination_location = pkg["destination"]

            # Add the distance to the warehouse and then to the customer.
            total_distance += euclidean_distance(current_location, warehouse_location)
            total_distance += euclidean_distance(warehouse_location, destination_location)

            # The next delivery starts from this destination.
            current_location = destination_location

        delivered = len(agent_packages)
        # A lower average distance means better efficiency.
        efficiency = round(total_distance / delivered, 2) if delivered else 0.0

        report[agent_id] = {
            "packages_delivered": delivered,
            "total_distance": round(total_distance, 2),
            "efficiency": efficiency,
        }

    return report


def pick_best_agent(report):
    """Find the agent with the lowest average distance per delivery."""
    delivering_agents = {
        agent_id: details for agent_id, details in report.items()
        if details["packages_delivered"] > 0
    }

    if not delivering_agents:
        return None

    return min(
        delivering_agents,
        key=lambda agent_id: delivering_agents[agent_id]["efficiency"]
    )


def add_random_delivery_delays(assignments, max_minutes=30, seed=None):
    """Bonus feature: add a repeatable random waiting time for each delivery."""
    rng = random.Random(seed)
    delay_log = {}

    for agent_id, agent_packages in assignments.items():
        delay_log[agent_id] = []

        for pkg in agent_packages:
            delay_minutes = rng.randint(0, max_minutes)
            delay_log[agent_id].append({
                "package_id": pkg["id"],
                "warehouse": pkg["warehouse"],
                "delay_minutes": delay_minutes,
            })

    return delay_log


# Step 5: Put everything together
def run_simulation(input_path, output_path="report.json"):
    """Main function: run the whole simulation and save the result."""
    warehouses, agents, packages = load_data(input_path)

    assignments = assign_packages_to_agents(warehouses, agents, packages)
    report = simulate_deliveries(warehouses, agents, assignments)
    report["best_agent"] = pick_best_agent(report)

    # Keep the bonus delays separate so report.json keeps the required format.
    delivery_delays = add_random_delivery_delays(assignments, seed=42)

    # Make sure the report contains one delivery count for every package.
    total_delivered = sum(
        details["packages_delivered"]
        for key, details in report.items()
        if key != "best_agent"
    )

    assert total_delivered == len(packages), (
        f"Something is wrong: {total_delivered} delivered but {len(packages)} expected"
    )

    # Save the completed report in the requested output file.
    with open(output_path, "w") as output_file:
        json.dump(report, output_file, indent=2)

    # Save the bonus output in its own JSON file.
    with open("delivery_delays.json", "w") as delay_file:
        json.dump(delivery_delays, delay_file, indent=2)

    return report


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python delivery_system.py <data.json> [report.json]")
        sys.exit(1)

    input_file = sys.argv[1]
    # Use the second command-line value as the report filename if provided.
    output_file = sys.argv[2] if len(sys.argv) > 2 else "report.json"

    # Catch common input and output errors and show a short message.
    try:
        result = run_simulation(input_file, output_file)
        print(json.dumps(result, indent=2))
        print(f"\nReport saved to {output_file}")
    # The input file does not exist.
    except FileNotFoundError:
        print(f"Error: input file '{input_file}' was not found.")
        sys.exit(1)
    # The file contents are not valid JSON.
    except json.JSONDecodeError:
        print(f"Error: '{input_file}' does not contain valid JSON.")
        sys.exit(1)
    # A required section or field is missing.
    except KeyError as error:
        print(f"Error: required data is missing from the JSON file: {error}")
        sys.exit(1)
    # The data is not valid or the package count does not match.
    except (ValueError, AssertionError) as error:
        print(f"Error: {error}")
        sys.exit(1)
    # There was a problem while saving the report.
    except OSError as error:
        print(f"Error: could not save the report: {error}")
        sys.exit(1)
