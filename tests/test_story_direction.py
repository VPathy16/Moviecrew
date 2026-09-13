import json
from copy import deepcopy
import pytest
from moviecrew.crew import MovieCrew, PipelineError
from moviecrew.mock import MockLLMClient
from moviecrew.schema import Shot
from moviecrew.story_direction import check_sequence


def everest_shots():
    labels=['secure','testing','falling','suspended','anchor_checked']
    actions=['Tests the foothold','Foothold breaks and she falls','Rope arrests her fall','She checks the damaged anchor']
    return [dict(id=f'sc1-sh{i+1}',scene_id='sc1',description=action,duration_s=3,
                 story_contract_version=1,purpose=['Establish risk','Trigger danger','Survive','Reveal remaining risk'][i],
                 action=action,entry_state={'climber':labels[i]},exit_state={'climber':labels[i+1]},
                 transition='cut') for i,action in enumerate(actions)]


class StoryLLM(MockLLMClient):
    def __init__(self,order=None):self.calls=[];self.order=order
    def complete_json(self,**kw):
        data=json.loads(kw['user']);self.calls.append((kw['task'],deepcopy(data)))
        if kw['task']=='cinematographer':return {'shots':everest_shots()}
        if kw['task']=='writer':
            return {'scenes':[dict(id='sc1',slug='everest',title='The foothold',summary='Survival creates a new risk',
                                  character_ids=['ch1'],location_id='loc1',event='A foothold fails',goal='Reach safety',
                                  obstacle='Unstable rock',turning_point='The anchor is damaged',acting_tasks={'ch1':'Test the rock with her boot'})]}
        if kw['task']=='editor':
            order=self.order or data['shot_ids'];return {'order':order,'chains':[[x] for x in order],
                'editorial_notes':{x:'Cut to the consequence of the preceding action' for x in order}}
        if kw['task']=='prompter':return {'prompts':[{'shot_id':data['shot']['id'],'prompt':data['shot']['action']}]}
        return super().complete_json(**kw)


def test_editor_and_prompter_receive_causal_context():
    llm=StoryLLM();film=MovieCrew(llm).make('A solo climber',run_continuity=False)
    editor=next(v for k,v in llm.calls if k=='editor')
    assert editor['context']['scenes'][0]['goal']=='Reach safety'
    assert editor['context']['scenes'][0]['shots'][1]['entry_state']=={'climber':'testing'}
    prompts=[v for k,v in llm.calls if k=='prompter']
    assert prompts[0]['context']['previous_shot'] is None
    assert prompts[1]['context']['previous_shot']['action']=='Tests the foothold'
    assert prompts[1]['context']['next_shot']['action']=='Rope arrests her fall'
    assert prompts[-1]['context']['next_shot'] is None
    assert prompts[1]['context']['world_descriptors']['characters'][0]['id']=='ch1'
    saved=deepcopy(film.render_plan.intents[1].direction_context)
    film.scenes[0].shots[0].action='Changed afterwards'
    assert film.render_plan.intents[1].direction_context==saved
    assert film.render_plan.intents[1].compiler_version=='story-direction-v1'
    assert film.render_plan.editorial_notes
    assert json.loads(film.to_json())['render_plan']['intents'][1]['direction_context']==saved


def test_reordered_cause_is_rejected_before_prompt_generation():
    llm=StoryLLM(['sc1-sh2','sc1-sh1','sc1-sh3','sc1-sh4'])
    with pytest.raises(PipelineError,match='conflicting entry state'):MovieCrew(llm).make('A climber')
    assert not any(k=='prompter' for k,_ in llm.calls)


def test_ellipsis_allows_intentional_time_change():
    shots=[Shot(**s) for s in everest_shots()]
    shots[1].entry_state={'climber':'later'}
    with pytest.raises(ValueError,match='conflicting'):check_sequence(shots,[s.id for s in shots])
    shots[1].transition='ellipsis'
    assert not check_sequence(shots,[s.id for s in shots])


@pytest.mark.parametrize('patch',[{'action':''},{'entry_state':{}},{'exit_state':{'climber':1}},{'transition':'nonsense'}])
def test_versioned_direction_rejects_missing_or_invalid_state(patch):
    data=everest_shots()[0];data.update(patch)
    with pytest.raises(ValueError):Shot(**data)


def test_legacy_shots_remain_readable_and_explicitly_unreviewed():
    shot=Shot(id='old',scene_id='s',description='Old shot',duration_s=3)
    flags=check_sequence([shot],['old'])
    assert flags and 'Legacy' in flags[0].message
