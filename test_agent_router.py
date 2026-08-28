from creative.agent import AugeoAgent
from creative.capabilities.defaults import build_registry


def test_agent_routes_website_requests():
    agent = AugeoAgent(registry=build_registry())

    result = agent.handle(
        "make a website for my barber shop",
        context={"title": "Northside Barber"},
    )

    assert result.task.capability == "website"
    assert result.output["artifact_type"] == "website"
    assert result.output["path"].endswith("output/websites/latest")


def test_agent_routes_pdf_requests():
    agent = AugeoAgent(registry=build_registry())

    result = agent.handle(
        "turn these into a PDF catalogue",
        context={"title": "Summer Catalogue"},
    )

    assert result.task.capability == "pdf"
    assert result.output["artifact_type"] == "pdf"
