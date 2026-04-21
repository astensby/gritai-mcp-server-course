import random
from datetime import date

from fastmcp import FastMCP
from fastmcp.apps.generative import GenerativeUI

mcp = FastMCP("population-generative-server")
mcp.add_provider(GenerativeUI())


@mcp.tool()
def get_population_history(country: str = "Norway") -> list[dict]:
    """Return 10 years of randomly generated population data for a country.

    Pair this with the generate_prefab_ui tool to render the result as
    any UI the model chooses (chart, table, cards, etc.).

    Args:
        country: Name of the country to generate data for.
    """
    current_year = date.today().year
    base_population = random.randint(1_000_000, 100_000_000)

    history = []
    population = base_population
    for year in range(current_year - 9, current_year + 1):
        growth = random.uniform(-0.01, 0.02)
        population = int(population * (1 + growth))
        history.append({"year": str(year), "country": country, "population": population})

    return history


if __name__ == "__main__":
    mcp.run(transport="stdio")
