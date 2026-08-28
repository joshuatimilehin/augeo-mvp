from creative.agent import AugeoAgent


def test_agent_exposes_capability_specs():
    agent = AugeoAgent()
    specs = agent.capability_specs()

    assert any(spec["name"] == "website" for spec in specs)
    assert any(spec["name"] == "pdf" for spec in specs)
    assert any(spec["name"] == "game" for spec in specs)


def test_agent_plan_has_capability_and_schema():
    agent = AugeoAgent()
    plan = agent.plan("Make a website for my barber shop", {"title": "Northside Barber"})

    assert plan["capability"] == "website"
    assert "title" in plan["required_context"]
    assert "website" in plan["capability"]
