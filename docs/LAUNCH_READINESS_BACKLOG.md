# Augeo Launch Readiness Backlog

This is the short, concrete pre-launch backlog for the architecture we are converging on: Astra GPT 6 is the primary brain, Fable 5.1 is the fallback, and the product should behave like a creative operating layer rather than a single-purpose generator.

## 1) Must-have before launch

### A. Unified orchestration brain
- [ ] Implement a single CreativeJob model that carries intent, subject, audience, context, desired effect, medium, format, constraints, references, creative direction, production plan, generation requirements, and approval state.
- [ ] Make the orchestration flow: conversation -> context -> intent -> creative job -> planning -> routing -> generation -> critique -> revision -> approval -> delivery -> learning.
- [ ] Ensure all content types (flyers, social, UGC, launch video, campaign concepts, etc.) enter the same job pipeline.
- [ ] Standardize a single status machine for draft -> ideation -> direction -> revision -> approved -> final.

### B. Multimodal context ingestion
- [ ] Add text context ingestion from chat conversations.
- [ ] Add image ingestion and understanding for product shots, reference visuals, and inspiration boards.
- [ ] Add URL ingestion and extraction for product pages, campaigns, articles, social references, and competitor examples.
- [ ] Add voice transcription and intent extraction from WhatsApp/iMessage voice notes.
- [ ] Add video reference ingestion for style and narrative analysis.
- [ ] Build a single context bundle combining text + media + web references + user intent.

### C. Reference intelligence
- [ ] Distinguish exact-match references from emotional references from inspiration references.
- [ ] Extract composition, pacing, tone, typography, color, product treatment, and emotional effect without copying.
- [ ] Add originality safeguards so the system can reference style without reproducing source content.
- [ ] Add explicit logic for “this is close to what I want” versus “this is only the feeling I want.”

### D. Model routing
- [ ] Implement a task-aware Model Router for image, video, audio, and editing tasks.
- [ ] Rank models by quality, suitability, cost, latency, consistency, and controllability.
- [ ] Default to Astra GPT 6 as the primary planner/reasoning brain.
- [ ] Keep Fable 5.1 as a fallback reasoning or recovery model.
- [ ] Support provider-specific routing without making Augeo depend on one vendor.

### E. Creative evaluation loop
- [ ] Add a Generation -> Critique -> Revise -> Regenerate loop.
- [ ] Define evaluation criteria: brief alignment, original taste, audience fit, product preservation, visual hierarchy, emotional effect, commercial fit.
- [ ] Add human-readable critique output: what is working, what is weak, what should change.
- [ ] Add revision planning from critique into concrete production changes.
- [ ] Record whether revision improves output.

### F. Human approval as a first-class state
- [ ] Treat approval as part of the creative job state, not a UI afterthought.
- [ ] Support user feedback: “yes,” “less corporate,” “only keep lighting,” “change pacing,” etc.
- [ ] Update the creative job state based on approved edits instead of restarting the workflow.
- [ ] Persist revision history so users can iterate without losing context.

### G. Memory beyond brand memory
- [ ] Expand memory from brand-only to person-level and project-level memory.
- [ ] Track creative preferences, taste, project history, recurring audiences, and collaborative memory.
- [ ] Allow a business to live inside a broader user/person model without a brittle business-only abstraction.
- [ ] Persist learned preferences for future recommendations and creative judgment.

### H. Security and usage economics
- [ ] Add auth and authorization for user and admin surfaces.
- [ ] Isolate API keys per provider and per environment.
- [ ] Add rate limiting and abuse prevention.
- [ ] Add input validation and webhook verification.
- [ ] Add payment verification and idempotency controls.
- [ ] Add generation quotas and token/credit accounting.
- [ ] Add provider cost tracking and actual-vs-estimated cost comparison.
- [ ] Add audit logs for usage, charges, and generation outcomes.

### I. Validation and benchmark research
- [ ] Create a benchmark comparing traditional workflow versus contextual Augeo workflow on the same brief.
- [ ] Use blind evaluation for quality comparisons.
- [ ] Measure completion rate, revision count, time to acceptable result, and perceived originality.
- [ ] Run a small real user test cohort before expansion.
- [ ] Use the LIGDOL exploration as a formal research and validation effort, not just a demo narrative.

## 2) Already partially in place

These are important building blocks already in the repo and should be treated as foundations, not completion:

- [x] Default intelligence model priority is now Astra GPT 6 with Fable fallback in config and provider wiring.
- [x] Basic provider abstraction exists for reasoning/intelligence.
- [x] Revision/session logic exists in the creative reasoning package.
- [x] Credit and billing scaffolding exists in the core database and app layer.
- [x] Creative job/state records already exist in the database.
- [x] Media provider abstraction exists for image/video/audio generation paths.

## 3) Deferred / do not expand yet

These are not launch blockers, but they are also not the next thing to build until the launch gate above is implemented:

- [ ] New standalone content feature categories without a shared CreativeJob abstraction.
- [ ] Another vendor-specific app mode (Seedance mode, Fable mode, Runway mode) as a product surface.
- [ ] Additional content templates before the core creative engine is stable.
- [ ] More spreadsheet-style dashboards or disconnected workflow UIs before the actual orchestration layer is solid.

## 4) Recommended execution order

1. CreativeJob abstraction
2. Multimodal context bundle
3. Reference intelligence
4. Model router
5. Critique/revision loop
6. Approval state and memory updates
7. Security + economics layer
8. Validation benchmark
9. Soft-launch cohort
10. Public launch

## 5) Final principle

The product should not become “40 disconnected capabilities.” It should become one coherent intelligence layer where the job changes, but the brain remains the same.

If the job is a football launch video, a premium handbag ad, a short film concept, or a social campaign, it should all flow through the same core system:

conversation -> context -> intent -> creative job -> planning -> routing -> generation -> critique -> revision -> approval -> delivery -> learning.
