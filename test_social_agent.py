from social_agent import SocialAgent


def test_agent_routes_tagged_ugc_request():
    request = SocialAgent().classify("@Augeo create a UGC script for handmade bags")
    assert request and request.capability == "ugc"
    result = SocialAgent().execute(request)
    assert result["status"] == "ready"
    assert "Hook" in result["content"]


def test_agent_routes_tagged_website_request():
    request = SocialAgent().classify("@Augeo make a website for my barber shop")
    assert request and request.capability == "website"
    result = SocialAgent().execute(request, context={"title": "Northside Barber"})
    assert result["status"] == "ready"
    assert result["artifact_type"] == "website"
    assert result["path"].endswith("output/websites/latest")


def test_agent_routes_tagged_code_request():
    request = SocialAgent().classify("@Augeo write a Python function to sum two numbers")
    assert request and request.capability == "code"
    result = SocialAgent().execute(request)
    assert result["status"] == "ready"
    assert "def" in result["content"].lower()


def test_agent_makes_image_requests_collectible_not_a_false_promise():
    request = SocialAgent().classify("Augeo, create an image for my new shoes")
    result = SocialAgent().execute(request)
    assert result["status"] == "needs_asset"
    assert "photo" in result["message"].lower()
