import json
from moviecrew.brief import BriefedLLM
from moviecrew.crew import MovieCrew
from moviecrew.mock import MockLLMClient
from moviecrew.studio import StudioSession, Stage
from moviecrew.image import MockImageProvider
from moviecrew import projects


def test_every_role_receives_saved_brief(tmp_path, monkeypatch):
    seen=[]
    class RecordingClient(MockLLMClient):
        def complete_json(self, *, task, system, user):
            seen.append((task,json.loads(user),system))
            return super().complete_json(task=task,system=system,user=user)
    brief={'film_type':'Short film','genre':'Mystery drama','language':'Tamil',
           'movie_references':['Arrival'],'reference_notes':'Quiet pacing','concept':'A keeper.'}
    project=MovieCrew(BriefedLLM(RecordingClient(),brief)).make('A keeper.')
    assert {row[0] for row in seen} == {'director','writer','designer','cinematographer','editor','prompter','continuity'}
    assert all(row[1]['film_brief']==brief for row in seen)
    monkeypatch.setenv('MOVIECREW_PROJECTS_ROOT',str(tmp_path))
    session=StudioSession('brief-film',Stage.SHOT_DEFS,project,str(tmp_path/'film'),MockImageProvider(),creative_brief=brief)
    projects.save(session)
    assert projects.load('brief-film',MockImageProvider()).creative_brief==brief
