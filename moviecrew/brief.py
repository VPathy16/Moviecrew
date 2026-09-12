"""Carry the opening film brief to every creative crew role."""
import json
from .llm import LLMClient


class BriefedLLM(LLMClient):
    def __init__(self, client, brief, world=None):
        self.client = client
        self.brief = brief
        self.world = world

    def complete_json(self, *, task, system, user):
        payload = json.loads(user)
        payload['film_brief'] = self.brief
        if self.world is not None:
            payload['approved_cast_and_world'] = self.world
        instructions = (
            '\nUse film_brief as the shared creative brief for your role. Respect its '
            'film type, genre and language throughout the story and visual decisions. '
            'Write narrative descriptions and any intended dialogue in the requested '
            'language; keep required JSON keys and identifier conventions unchanged. '
            'If the language is No dialogue, use English production descriptions '
            'and plan no spoken dialogue. '
            'Movie references guide tone, pacing and visual qualities; create an '
            'original story rather than reproducing their characters or plot. '
            'Do not invent dialogue, soundtrack or production features your output '
            'schema does not support. Preserve the required output schema.'
        )
        return self.client.complete_json(task=task, system=system+instructions,
                                         user=json.dumps(payload, ensure_ascii=False))
