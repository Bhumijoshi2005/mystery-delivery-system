# FastBox Delivery System

## My solution

I made this Python program to simulate one day of deliveries for FastBox. It
reads the warehouses, agents, and packages from `data.json`. For each package,
it finds the agent closest to the package warehouse and assigns the package to
that agent.

After the assignment, I simulate the route of each agent. The program then
calculates the total distance, number of delivered packages, and average
distance per package. Finally, it saves the result in `report.json`.

## Main features

- Reads JSON data using Python's built-in `json` module.
- Calculates straight-line distance using the Euclidean distance formula.
- Assigns each package to the nearest agent.
- Calculates total distance for every agent.
- Calculates efficiency as average distance per delivered package.
- Finds the most efficient agent using the lowest efficiency value.
- Checks that the number of delivered packages matches the input package count.

## Bonus features I added

- Adds a simulated random delay for every package. A fixed seed is used so
	repeated runs give the same delay values.

The delay data is saved separately in `delivery_delays.json` so that the main
`report.json` keeps the same structure as the required sample output.
The main report contains one section for each agent and a `best_agent` value.
The delay file is only for the extra bonus feature.

## Assumptions for unclear cases

The assignment does not define every possible situation. I used the following
assumptions for unspecified cases:

1. Packages are delivered in the same order as they appear in `data.json`.

2. For each package, the agent travels from the current position to the
	warehouse and then from the warehouse to the package destination.

3. After the last delivery, the agent does not return to a warehouse because
	the report measures delivery travel only.

4. If two agents are the same distance from a warehouse, I select the agent
	that appears first in the input JSON. This gives a consistent result.

5. Packages belonging to the same warehouse are assigned to the same nearest
	agent.

6. An agent with no assigned packages has zero efficiency in the report, but I
	exclude it when selecting the best agent. Otherwise, zero could incorrectly
	look better than the efficiency of an agent that actually delivered packages.

7. If there are no deliveries, the best agent is reported as `null`.

8. I use a fixed random seed for delays so that repeated runs produce the same
	delay values and can be tested easily.

9. The input must contain warehouses, agents, and packages in the expected JSON
	format. Missing or unsupported data causes the program to show an error
	instead of producing an incorrect report.

## How I run the program

I first open the project folder:

```text
cd fastbox-delivery-system
```

Then I run the current input file and save its output with this command:

```text
python delivery_system.py data.json report.json
```

Here, `data.json` is the input file and `report.json` is the output report.

If I do not provide an output filename, the program uses `report.json` by
default:

```text
python delivery_system.py data.json
```

To run one of the extra test cases, I use its path inside the `test_cases`
folder:

```text
cd "c:\Users\A2IN\OneDrive\Desktop\Python Assignment -2026\fastbox-delivery-system"
python delivery_system.py test_cases/test_case_1.json test_report_1.json
```
Similarly, we can use the above command for other test cases as well. In this project i have checked and stored reports of only test_case_1,test_case_2 and test_case_3 and its report are also stores as test_report_1 and so on.

## Technologies used

- Python 3
- JSON files for input and output
- Python built-in modules: `json`, `math`, `random`, and `sys`
