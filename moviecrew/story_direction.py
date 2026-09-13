"""Versioned planning context. This records intent, not proof of rendered continuity."""
from copy import deepcopy
from dataclasses import asdict
from .schema import ContinuityFlag

COMPILER_VERSION = 'story-direction-v1'


def check_sequence(shots, order, *, strict=True):
    by_id = {s.id:s for s in shots}
    flags = []
    previous = None
    for sid in order:
        shot = by_id[sid]
        if not shot.story_contract_version:
            flags.append(ContinuityFlag(sid, 'warning', 'Legacy shot has no explicit causal direction; review its action and state before generation.'))
        elif previous and previous.story_contract_version and previous.scene_id==shot.scene_id and shot.transition!='ellipsis':
            contradictions = [key for key in shot.entry_state if key in previous.exit_state and previous.exit_state[key]!=shot.entry_state[key]]
            if contradictions:
                message = f'{previous.id} → {sid}: conflicting entry state for {", ".join(contradictions)}; review whether the transition is intentional.'
                if strict:
                    raise ValueError(message)
                flags.append(ContinuityFlag(sid, 'warning', message))
            if previous.action.strip().casefold()==shot.action.strip().casefold():
                flags.append(ContinuityFlag(sid,'warning','Adjacent shots repeat the same action. Check that this is intentional coverage, not a repeated event.'))
        previous = shot
    return flags


def prompt_context(shot, scenes, order, bible, title, logline, outline, editorial_notes, world_approved=False):
    by_id = {s.id:s for scene in scenes for s in scene.shots}
    scene = next(s for s in scenes if s.id==shot.scene_id)
    index = order.index(shot.id)
    def adjacent(offset):
        i = index+offset
        return asdict(by_id[order[i]]) if 0<=i<len(order) else None
    # Descriptors remain separate from execution-time reference resolution. Do not
    # claim that these assets were attached to a provider or visually obeyed.
    assets = bible.to_dict()
    assets['characters'] = [c for c in assets['characters'] if c['id'] in scene.character_ids]
    assets['locations'] = [l for l in assets['locations'] if l['id']==scene.location_id]
    return deepcopy({
        'compiler_version': COMPILER_VERSION,
        'film': {'title':title,'logline':logline,'outline':outline},
        'scene': {k:v for k,v in asdict(scene).items() if k!='shots'},
        'previous_shot': adjacent(-1), 'next_shot': adjacent(1),
        'current_shot': asdict(shot),
        'editorial_note': editorial_notes.get(shot.id,''),
        'world_descriptors': assets,
        'world_approved': world_approved,
        'reference_note':'Planning descriptors only; actual image bindings are resolved at generation time.',
    })
