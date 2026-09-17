from typing import Any, Dict

from creative.experience.actions import ActionPlan
from creative.experience.intent import CreativeIntent
from creative.experience.session import ExperienceSession


class CreativeDirector:
    """
    Converts human creative requests into structured intent
    and executable creative actions.

    This is intentionally provider-agnostic.
    """

    def understand(
        self,
        request: str,
        session: ExperienceSession,
    ) -> CreativeIntent:
        request_lower = request.lower()

        intent = CreativeIntent(
            raw_request=request,
            confidence=0.5,
        )

        if any(
            word in request_lower
            for word in [
                "video",
                "film",
                "reel",
                "animation",
            ]
        ):
            intent.medium = "video"

        elif any(
            word in request_lower
            for word in [
                "image",
                "poster",
                "flyer",
                "visual",
                "graphic",
            ]
        ):
            intent.medium = "image"

        if any(
            word in request_lower
            for word in [
                "launch",
                "campaign",
                "advert",
                "ad",
                "promo",
            ]
        ):
            intent.goal = "promotion"

        if any(
            word in request_lower
            for word in [
                "luxury",
                "premium",
                "cinematic",
                "minimal",
                "editorial",
                "bold",
            ]
        ):
            intent.style = " ".join(
                word
                for word in [
                    "luxury" if "luxury" in request_lower else "",
                    "premium" if "premium" in request_lower else "",
                    "cinematic" if "cinematic" in request_lower else "",
                    "minimal" if "minimal" in request_lower else "",
                    "editorial" if "editorial" in request_lower else "",
                    "bold" if "bold" in request_lower else "",
                ]
                if word
            )

        intent.context["session_id"] = session.session_id

        if (
            intent.medium
            or intent.goal
            or intent.style
        ):
            intent.confidence = 0.8

        return intent

    def plan(
        self,
        intent: CreativeIntent,
        session: ExperienceSession,
    ) -> ActionPlan:
        plan = ActionPlan()

        if intent.medium == "image":
            plan.add(
                "create_image",
                {
                    "goal": intent.goal,
                    "style": intent.style,
                    "context": intent.context,
                },
            )

        elif intent.medium == "video":
            plan.add(
                "create_video",
                {
                    "goal": intent.goal,
                    "style": intent.style,
                    "context": intent.context,
                },
            )

        else:
            plan.add(
                "clarify",
                {
                    "question": "What would you like to create?",
                },
            )

        return plan

    def direct(
        self,
        request: str,
        session: ExperienceSession,
    ) -> Dict[str, Any]:
        session.add_message("user", request)

        intent = self.understand(
            request,
            session,
        )

        session.set_intent(
            intent.to_dict()
        )

        plan = self.plan(
            intent,
            session,
        )

        session.update_state(
            last_request=request,
            last_plan=plan.to_dict(),
        )

        return {
            "intent": intent.to_dict(),
            "plan": plan.to_dict(),
            "session": session.snapshot(),
        }