import os

from dotenv import load_dotenv

from creative.context import CustomerContext
from creative.image.ideogram import IdeogramProvider


load_dotenv()


details = {
    "product_name": "Luxury Black Leather Handbag",
    "brand_name": "Augeo Test Brand",
    "audience": "young professionals and affluent Nigerian customers",
    "location": "Nigeria",
    "niche": "luxury fashion",
    "intent": "product advertisement",
    "occasion": "everyday luxury",
}


context = CustomerContext.from_order(
    details=details,
    graphic_skill_name="skill-luxury",
    prompt_skill_name="skill-english-market",
    category_skill_name="skill-fashion",
    product_description=(
        "A sophisticated premium black leather handbag "
        "with an elegant minimalist design."
    ),
    price_text="₦85,000",
)


prompt = """
Create a premium commercial fashion advertisement for a Nigerian
luxury fashion brand.

PRODUCT:
Luxury black leather handbag.

PRODUCT DESCRIPTION:
A sophisticated premium black leather handbag with an elegant
minimalist design.

TARGET CUSTOMER:
Young professionals and affluent Nigerian customers.

LOCATION:
Nigeria.

VISUAL DIRECTION:
Luxury editorial fashion photography.
High-end Nigerian fashion campaign.
Dramatic studio lighting.
Elegant deep tones.
Premium product presentation.
Photorealistic leather texture.
Sophisticated composition.
Expensive and aspirational visual language.
Clean commercial advertising aesthetic.

TEXT:
Include the exact headline:
"TIMELESS. ELEVATED."

Include the exact price:
"₦85,000"

The text must be spelled exactly as provided.

Do not add unrelated products.
Do not add watermarks.
Do not use distorted typography.
Do not introduce additional prices.
Do not introduce fake brand claims.

The final image should look like a professionally designed
premium fashion advertisement suitable for social media.
"""


print("Creating Ideogram provider...")

provider = IdeogramProvider()

print("Generating image...")
print("This will make one real Ideogram API request.")


result = provider.generate(
    context=context,
    prompt=prompt,
)


image = result["image"]

output_path = "output/ideogram_test.png"

os.makedirs("output", exist_ok=True)

image.save(output_path)


print()
print("=" * 50)
print("IDEOGRAM GENERATION SUCCESSFUL")
print("=" * 50)
print(f"Provider:     {result['provider']}")
print(f"Model:        {result['model']}")
print(f"Seed:         {result['seed']}")
print(f"Resolution:   {result['resolution']}")
print(f"Safe:         {result['is_image_safe']}")
print(f"Saved to:     {output_path}")
print("=" * 50)