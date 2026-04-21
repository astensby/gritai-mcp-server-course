import random
from datetime import date

from fastmcp import FastMCP, FastMCPApp
from prefab_ui.actions import SetState, ShowToast
from prefab_ui.actions.mcp import CallTool
from prefab_ui.app import PrefabApp
from prefab_ui.components import (
    Button,
    Column,
    Form,
    Heading,
    Input,
    Row,
    Separator,
    Text,
)
from prefab_ui.components.charts import BarChart, ChartSeries
from prefab_ui.rx import RESULT, Rx

app = FastMCPApp("population-interactive")


def _generate_population_history(country: str) -> list[dict]:
    current_year = date.today().year
    base_population = random.randint(1_000_000, 100_000_000)

    history = []
    population = base_population
    for year in range(current_year - 9, current_year + 1):
        growth = random.uniform(-0.01, 0.02)
        population = int(population * (1 + growth))
        history.append({"year": str(year), "country": country, "population": population})

    return history


@app.tool()
def regenerate_population(country: str) -> dict:
    """Generate a fresh 10-year random population history for a country."""
    history = _generate_population_history(country)
    return {"country": country, "history": history}


@app.ui()
def population_viewer(country: str = "Norway") -> PrefabApp:
    """Open an interactive population viewer with a chart that can be
    regenerated for any country.

    Args:
        country: Country to show initial data for.
    """
    initial_history = _generate_population_history(country)

    with Column(gap=6, css_class="p-6") as view:
        Heading(Rx("country") + " — 10 Year Population")
        Text(
            "Randomly generated data. Enter a country and regenerate to refresh.",
            css_class="text-muted-foreground",
        )

        BarChart(
            data=Rx("history"),
            series=[ChartSeries(data_key="population", label="Population")],
            xAxis="year",
            height=320,
        )

        Separator()

        with Form(
            on_submit=CallTool(
                regenerate_population,
                arguments={"country": Rx("form_country")},
                on_success=[
                    SetState("country", RESULT["country"]),
                    SetState("history", RESULT["history"]),
                    ShowToast("Regenerated!", variant="success"),
                ],
                on_error=ShowToast("Failed to regenerate", variant="error"),
            )
        ):
            with Row(gap=2, align="end"):
                Input(name="form_country", label="Country", required=True)
                Button("Regenerate")

    return PrefabApp(
        view=view,
        state={
            "country": country,
            "form_country": country,
            "history": initial_history,
        },
    )


mcp = FastMCP("population-interactive-server", providers=[app])


if __name__ == "__main__":
    mcp.run(transport="stdio")
