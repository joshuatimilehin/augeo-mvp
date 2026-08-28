# Augeo

Augeo is an agent-native creative and business execution system.

The user should not need to understand models, prompts, design tools, website builders, PDF software, game engines, APIs, or technical workflows. They should be able to say what they want and have Augeo figure out how to make it happen.

The core product principle is simple:

Intent → Agent → Artifact / Action

Examples:

- “Make a premium F1 poster for my brand.”
- “Turn this product into a UGC ad.”
- “Build me a website for my restaurant.”
- “Make a PDF menu from this.”
- “Build a simple football game.”
- “Create three versions.”
- “Make it more premium.”
- “Post the best one tomorrow.”

Augeo is not a dashboard with AI buttons. It is the layer that turns ordinary human intent into finished work.

## Why this exists

The old thesis was focused on better creative generation for businesses. The stronger product thesis is broader:

Augeo is the system that lets ordinary people create and execute software-like output through conversation.

That includes:

- images
- campaign concepts
- UGC scripts
- social captions
- websites
- PDFs
- games
- business artifacts
- scheduled delivery
- revision flows
- brand-aware output

The artifact is secondary. The conversation is the interface.

## Product model

Augeo should feel like this:

- the user says a thing
- the agent understands intent
- the agent plans the task
- the agent selects the relevant capability
- the agent gathers context and brand memory
- the agent executes the work
- the agent returns the artifact or action
- the user revises only when necessary

This is far more important than a list of isolated features.

## What the repository already contains

The project already contains the strongest foundations for this direction:

- creative context and customer intelligence
- prompt retrieval and adaptation
- generation pipeline
- capability registry
- website generation capability
- PDF generation capability
- game generation capability
- social tag-to-create layer
- conversation routing layer
- provider abstraction for image generation
- memory-aware creative architecture

The key is not to throw this away. The key is to place it underneath a larger agent runtime.

## Current capabilities

The implemented system already supports the core execution loop:

- website generation
- PDF generation
- game generation
- social request classification
- conversational task routing
- follow-up handling for incomplete creative requests
- safe fallback behavior for provider failures

## Architectural direction

The system is organized around a task-first model:

Message
  ↓
Intent understanding
  ↓
Task planning
  ↓
Capability selection
  ↓
Execution
  ↓
Artifact
  ↓
Response / revision / delivery

The technical abstractions already reflect this direction:

- creative.agent contains the conversational router and task abstraction
- creative.capabilities contains the capability registry and execution contracts
- creative.artifacts handles artifact output and persistence
- creative.generation keeps the provider-driven generation pipeline
- social_agent provides the tag-to-create interface for messaging surfaces

## Message-first examples

The desired product flow is intentionally low-friction:

- “@Augeo make a UGC for this”
- “@Augeo make this into a website”
- “@Augeo turn these into a PDF”
- “@Augeo create 3 versions”
- “@Augeo make it more premium”
- “@Augeo use my brand style”
- “@Augeo post version 2 tomorrow”

The user should not need to know the model, renderer, prompt strategy, framework, or publishing backend. The agent handles that.

## Tag-to-create interface

The project includes a message-friendly route and capability surface:

- POST /agent/execute
- GET /agent/capabilities

A basic example is:

- instruction: “@Augeo create a UGC script for handmade bags”

The social flow classifies the request and routes it into the relevant task path.

## Development status

This repository is no longer best described as only a flyer generator.

It is better described as a working foundation for a creative-first agent system that can perform real digital work from plain-language intent.

The immediate goal is not to add random features. The immediate goal is to make the agent runtime solid, coherent, and extensible.

## Local setup

Install dependencies and activate the workspace environment before running tests.

Environment variables used by the current stack include:

- IDEOGRAM_API_KEY
- IMAGE_PROVIDER
- KASPO_API_KEY
- KASPO_BASE_URL
- PAYSTACK_SECRET_KEY
- OPENAI_API_KEY

The project is designed to fail gracefully when a provider is unavailable, so local development and testing remain usable even when external services are rate-limited or unconfigured.

## Validation

The project uses pytest for regression checks.

Current validation status:

- 14 passed
- 1 skipped

This verifies the agent routing, social request flow, and conversational task execution remain stable.

## Final north star

The real metric is not how many prompts were generated. The real metric is:

How much digital work can an ordinary person accomplish through one simple conversation?

That is the product direction for Augeo.

Augeo is not the software people learn to use.
Augeo is the agent that uses software on their behalf.
