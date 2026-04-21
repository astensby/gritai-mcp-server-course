import random
from datetime import date

from fastmcp import FastMCP
from fastmcp.tools import ToolResult
from prefab_ui.app import PrefabApp
from prefab_ui.components import Column, Heading, Text
from prefab_ui.components.charts import BarChart, ChartSeries

mcp = FastMCP("population-uiapp-server")


def _generate_population_history(country: str) -> list[dict]:
    current_year = date.today().year
    base_population = random.randint(1_000_000, 100_000_000)

    history = []
    population = base_population
    for year in range(current_year - 9, current_year + 1):
        growth = random.uniform(-0.01, 0.02)
        population = int(population * (1 + growth))
        history.append({"year": year, "country": country, "population": population})

    return history


@mcp.tool(app=True)
def get_population_history(country: str = "Norway") -> ToolResult:
    """Return 10 years of randomly generated population data for a country,
    rendered as an interactive bar chart.

    Args:
        country: Name of the country to generate data for.
    """
    data = _generate_population_history(country)

    start_year = data[0]["year"]
    end_year = data[-1]["year"]
    start_pop = data[0]["population"]
    end_pop = data[-1]["population"]
    change_pct = ((end_pop - start_pop) / start_pop) * 100

    summary = (
        f"{country} population from {start_year} to {end_year}: "
        f"{start_pop:,} -> {end_pop:,} ({change_pct:+.2f}%). "
        f"Full series: {data}"
    )

    with Column(gap=4, css_class="p-6") as view:
        Heading(f"{country} Population ({start_year}-{end_year})")
        Text(f"Change: {change_pct:+.2f}%")
        BarChart(
            data=data,
            series=[ChartSeries(data_key="population", label="Population")],
            x_axis="year",
        )

    return ToolResult(
        content=summary,
        structured_content=view,
    )


if __name__ == "__main__":
    mcp.run(transport="stdio")
