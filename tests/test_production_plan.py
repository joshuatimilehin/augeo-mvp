from creative.reasoning.director import CreativeDirector
from creative.context import CustomerContext
from creative.reasoning.directions import ideate_directions


def test_create_production_spec_includes_plan_for_video():
    director = CreativeDirector()
    context = CustomerContext(
        category='general',
        subcategory=None,
        product_name='TestProduct',
        product_description='A test product',
        price=None,
        brand_name='TestBrand',
        audience=None,
        location=None,
        language='english',
        visual_style='modern',
    )
    session = director.start(context, brief='Make a short social product video about the product')
    # Ideate and pick a candidate
    candidates = ideate_directions(context, brief=session.brief, n=1)
    assert candidates
    # Simulate selected_direction as a DirectionCandidate
    session.selected_direction = candidates[0]
    spec = director.create_production_spec(session, deliverable='short_video', aspect_ratio='16:9', variation_count=1)
    assert spec is not None
    assert spec.production_plan is not None
    assert isinstance(spec.production_plan.shots, list)
    assert len(spec.production_plan.shots) >= 1
    shot = spec.production_plan.shots[0]
    assert shot.description is not None
    assert shot.id == 'shot-1'
