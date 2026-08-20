# Augeo Brand Intelligence — V1

This is deliberately a thin layer above the existing creative intelligence
system.

## Components

- `creative/brand/profile.py` — persistent brand representation.
- `creative/brand/manager.py` — load/save brand memory, approved logo handling,
  creative context, and optional logo recommendation.
- `creative/brand/guard.py` — deterministic brand consistency/IP-risk checks.
- `test_brand_manager.py` — API-free tests.

## Approved logo rule

If a customer supplies a logo, Augeo stores the asset reference and treats it
as approved. Normal generation must use that exact asset reference. The Brand
Manager never redraws, stylizes, or "improves" an approved logo.

If no logo exists, the system may offer an optional logo-creation workflow.

## Integration point

The intended flow is:

CustomerContext
  -> BrandManager.get_profile()
  -> PromptRetriever
  -> CreativeOrchestrator
  -> GenerationProvider
  -> BrandGuard
  -> Evaluation / persistent learning

Do not replace the existing prompt library or orchestrator. This layer is
additive.

## Existing database compatibility

The current `brand_memory` table already has:
- business_name
- primary_color
- secondary_color
- logo_path
- preferred_language
- preferred_tone
- common_phrases
- avoid_words
- category_focus
- template_preference

Therefore V1 uses the existing schema rather than introducing another
database migration.

## Next integration

After copying these files into the repo:

    python -m pytest -q test_brand_manager.py

Then:

    python -m pytest -q

Only after these are green should the BrandManager be wired into the
orchestrator/layout prompt path.
