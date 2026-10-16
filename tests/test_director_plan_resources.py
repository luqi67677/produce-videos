"""资源门禁回归：规划不可许诺不存在的效果或声音，合成使用同一 EDL。"""
from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest
from unittest import mock
import wave

import test_director_plan as fixtures
from director_plan_resources import media_info
from validate_director_plan import validate
from export_director_board import render_board


class ExistingResourceTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixtures.DirectorPlanTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.tearDown)
        self.project = self.fixture.project
        self.data = self.fixture.data
        self.data['director_plan'].update(schema_version='1.1', effect_catalog=[])
        for shot in self.data['shots']:
            direction = shot['direction']
            direction.update(effects=[], events=[], assets_needed=[],
                             background={'mode':'static', 'description':'暖灰固定底色', 'reason':'保持文字清晰',
                                         'effect_instance_ids':[], 'intensity':'none', 'continuity':'沿用同一底色'},
                             music={'mode':'none', 'reason':'让旁白独立表达'})
        self.save()

    def write(self, name, data):
        self.fixture.write(name, data)

    def save(self):
        self.fixture.save()

    def effect(self, index=0, target='foreground'):
        implementation = self.project / 'existing-effect.py'
        implementation.write_text('def opacity(frame):\n    return min(1, frame / 30)\n', encoding='utf-8')
        artifact = self.project / 'prior-test.log'
        artifact.write_text('Previous run: opacity(0)=0; opacity(30)=1; passed\n', encoding='utf-8')
        proof = {'effect_id':'fade-existing', 'implementation_sha256':fixtures.digest(implementation), 'status':'passed',
                 'verification_method':'execution-test', 'details':'此前执行测试确认端点', 'command':'python -m unittest effect_test',
                 'artifact':{'path':artifact.name,'sha256':fixtures.digest(artifact)}}
        self.write('effect-proof.json', proof)
        catalog = {'effect_id':'fade-existing','library':'fixture-library','version':'1.0','source_url':'https://example.org/library', 'license':'MIT',
                   'implementation':{'path':implementation.name,'sha256':fixtures.digest(implementation),'entrypoint':'opacity'},
                   'availability':{'status':'verified','evidence_path':'effect-proof.json','evidence_sha256':fixtures.digest(self.project/'effect-proof.json')}}
        self.data['director_plan']['effect_catalog'] = [catalog]
        direction = self.data['shots'][index]['direction']
        iid = f'fade-{index}'
        direction['effects'] = [{'instance_id':iid,'effect_id':'fade-existing','target':target,'purpose':'让结果状态出现',
                                 'parameters':{},'start_trigger':'旁白提到结果','stop_trigger':'结果卡出现完整'}]
        event = fixtures.event(f'event-{index}', self.data['shots'][index]['narration_excerpt'])
        event['effect_instance_ids'] = [iid]
        direction['events'] = [event]
        if target == 'background':
            direction['background'].update(mode='animated',effect_instance_ids=[iid],intensity='subtle')
        self.save()
        return catalog, event

    def audio(self, aid='local-audio'):
        path = self.project / f'{aid}.wav'
        with wave.open(str(path),'wb') as stream:
            stream.setparams((1,2,8000,0,'NONE','not compressed'))
            stream.writeframes(b'\0\0' * 8000 * 12)
        proof = self.project / f'{aid}-rights.txt'
        proof.write_text('本测试夹具自行创建，可用于自动测试。',encoding='utf-8')
        item = {'asset_id':aid,'path':path.name,'sha256':fixtures.digest(path),
                'rights':{'status':'reviewed','basis':'self-created','license_name':'','source_url':'','license_url':'',
                          'evidence_path':proof.name,'evidence_sha256':fixtures.digest(proof),'allowed_use':'测试',
                          'restrictions_review':'仅测试夹具','attribution':{'required':False,'text':'','placement':''}}}
        source_file = self.project/'source-assets.json'
        source = json.loads(source_file.read_text()) if source_file.exists() else {'items':[]}
        source['items'] = [x for x in source['items'] if x['asset_id'] != aid] + [item]
        self.write('source-assets.json',source)
        return item

    def request(self, index, rid='audio-request', aid='local-audio'):
        request = fixtures.asset_request(rid,'音效或配乐')
        request['selected_asset_ids'] = [aid]
        self.data['shots'][index]['direction']['assets_needed'].append(request)
        return request

    def music(self, index=0, before=False, after=False):
        self.request(index)
        self.data['shots'][index]['direction']['music'] = {'mode':'track','reason':'支撑连续段落','request_id':'audio-request',
            'start_trigger':'段落开始','stop_trigger':'段落结束','gain_db':-22,'fade_in_ms':0,'fade_out_ms':0,
            'ducking':'旁白说话时压低','continuity':{'from_previous':before,'to_next':after}}
        self.save()

    def ready(self):
        self.data['director_plan'].update(stage='ready',timing_basis='measured')
        clips = []
        for index, shot in enumerate(self.data['shots']):
            direction = shot['direction']
            clip = {'clip_id':shot['shot_id'],'scene_id':shot['shot_id'],'timeline_start_seconds':index*3,'duration_seconds':3,
                    'narration_excerpt':shot['narration_excerpt'],'semantic_events':[],
                    'effect_cues':[{'instance_id':e['instance_id'],'start_frame':0,'end_frame':90} for e in direction['effects']]}
            for event in direction['events']:
                timed = {'event_id':event['event_id'],'start_frame':0,'end_frame':30}
                if event['sound']['mode'] != 'none':
                    timed['sound']={'asset_id':'local-audio','start_frame':0,'end_frame':90,'source_start_frame':index*90,
                                    'gain_db':-18,'fade_in_ms':0,'fade_out_ms':0}
                clip['semantic_events'].append(timed)
            if direction['music']['mode'] == 'track':
                clip['music_cue']={'asset_id':'local-audio','start_frame':0,'end_frame':90,'source_start_frame':index*90,
                                   'gain_db':-22,'fade_in_ms':0,'fade_out_ms':0}
            clips.append(clip)
        self.edl = {'schema_version':'1.1','format':{'fps':30},'picture_track':clips}
        self.write('edit-decision-list.json',self.edl)
        self.save()

    def errors(self):
        self.save()
        return validate(self.project)

    def test_static_silent_plan_remains_possible_without_media(self):
        self.assertEqual(self.errors(), [])
        board = render_board(self.project)
        self.assertIn('背景：静止',board)
        self.assertIn('配乐：不使用',board)
        self.assertIn('预计总时长',board)
        self.assertFalse((self.project/'source-assets.json').exists())

    def test_legacy_contract_still_accepts_unchanged_planning_and_ready(self):
        legacy = fixtures.DirectorPlanTests()
        legacy.setUp()
        self.addCleanup(legacy.tearDown)
        self.assertEqual(validate(legacy.project), [])
        legacy.ready()
        self.assertEqual(validate(legacy.project, require_ready=True), [])

    def test_downgrading_version_cannot_hide_new_resource_fields(self):
        self.effect()
        self.data['director_plan']['schema_version'] = '1.0'
        (self.project/'existing-effect.py').unlink()
        self.assertTrue(any('1.1 专属字段' in error for error in self.errors()))

    def test_each_new_plan_field_is_rejected_in_legacy_contract(self):
        legacy = fixtures.DirectorPlanTests()
        legacy.setUp()
        self.addCleanup(legacy.tearDown)
        baseline = copy.deepcopy(legacy.data)
        cases = [
            ('plan', 'effect_catalog', []),
            ('direction', 'effects', []),
            ('direction', 'background', {'mode':'static'}),
            ('direction', 'music', {'mode':'none'}),
            ('event', 'kind', 'effect'),
            ('event', 'effect_instance_ids', []),
            ('event', 'source_request_id', 'person'),
            ('sound', 'continuity', {'from_previous':False, 'to_next':False}),
        ]
        for location, key, value in cases:
            with self.subTest(location=location, key=key):
                legacy.data = copy.deepcopy(baseline)
                direction = legacy.data['shots'][0]['direction']
                targets = {'plan':legacy.data['director_plan'], 'direction':direction,
                           'event':direction['events'][0], 'sound':direction['events'][0]['sound']}
                targets[location][key] = value
                legacy.save()
                self.assertTrue(any(f'.{key} 是 director_plan 1.1 专属字段' in error
                                    for error in validate(legacy.project)))

    def test_new_edl_resource_fields_cannot_hide_in_legacy_ready_plan(self):
        legacy = fixtures.DirectorPlanTests()
        legacy.setUp()
        self.addCleanup(legacy.tearDown)
        legacy.ready()
        baseline = copy.deepcopy(legacy.edl)
        cases = [('clip', 'effect_cues', []), ('clip', 'music_cue', {}),
                 ('event', 'source_action', {}), ('sound', 'asset_id', 'whoosh'),
                 ('sound', 'source_start_frame', 0)]
        for location, key, value in cases:
            with self.subTest(location=location, key=key):
                edl = copy.deepcopy(baseline)
                clip = edl['picture_track'][0]
                targets = {'clip':clip, 'event':clip['semantic_events'][0],
                           'sound':clip['semantic_events'][0]['sound']}
                targets[location][key] = value
                legacy.write('edit-decision-list.json', edl)
                self.assertTrue(any(f'.{key} 是 director_plan 1.1 专属字段' in error
                                    for error in validate(legacy.project, require_ready=True)))

    def test_existing_effect_proof_binds_real_code_and_nonempty_artifact(self):
        catalog, _ = self.effect(target='background')
        self.assertEqual(self.errors(), [])
        with mock.patch('director_plan_resources.subprocess.run',side_effect=AssertionError('不得执行效果')):
            self.assertEqual(self.errors(), [])
        (self.project/'prior-test.log').write_text('changed',encoding='utf-8')
        self.assertTrue(any('SHA-256' in e for e in self.errors()))
        (self.project/'prior-test.log').write_text('',encoding='utf-8')
        self.assertTrue(any('为空' in e for e in self.errors()))
        self.assertIn('已有实现',render_board_for_valid_effect(self))

    def test_document_cannot_be_registered_as_effect_implementation(self):
        catalog, _ = self.effect()
        path=self.project/'description.md'
        path.write_text('效果将在未来实现。',encoding='utf-8')
        catalog['implementation'].update(path=path.name,sha256=fixtures.digest(path))
        self.assertTrue(any('实现' in e for e in self.errors()))

    def test_unavailable_effect_and_event_cannot_bypass_catalog(self):
        _, event = self.effect()
        event['effect_instance_ids']=['fictional']
        self.assertTrue(any('已有动效实例' in e for e in self.errors()))
        event['effect_instance_ids']=['fade-0']
        self.data['director_plan']['effect_catalog']=[]
        self.assertTrue(any('未登记' in e for e in self.errors()))

    def test_selected_music_requires_real_audio_and_rights_during_planning(self):
        item=self.audio()
        self.music()
        self.assertEqual(self.errors(),[])
        path=self.project/item['path']
        path.write_text('not audio',encoding='utf-8')
        item['sha256']=fixtures.digest(path)
        self.write('source-assets.json',{'items':[item]})
        self.assertTrue(any('真实本地音频' in e for e in self.errors()))
        item=self.audio()
        (self.project/item['rights']['evidence_path']).unlink()
        self.assertTrue(any('证据' in e for e in self.errors()))

    def test_sound_cannot_be_a_future_download(self):
        _, event=self.effect()
        request=self.request(0)
        request['selected_asset_ids']=[]
        event['sound']={'mode':'sfx','reason':'任务交接','request_id':'audio-request','start_trigger':'交接','stop_trigger':'完成'}
        self.assertTrue(any('待搜索声音' in e for e in self.errors()))
        self.audio()
        request['selected_asset_ids']=['local-audio']
        self.assertEqual(self.errors(),[])

    def test_ready_effect_cues_must_match_instances_and_fit_clip(self):
        self.effect()
        self.ready()
        self.assertEqual(self.errors(),[])
        self.edl['picture_track'][0]['effect_cues'][0]['end_frame']=91
        self.write('edit-decision-list.json',self.edl)
        self.assertTrue(any('范围' in e for e in self.errors()))
        self.edl['picture_track'][0]['effect_cues']=[]
        self.write('edit-decision-list.json',self.edl)
        self.assertTrue(any('一一对应' in e for e in self.errors()))

    def test_bound_effect_cues_must_overlap_their_semantic_event(self):
        self.effect()
        self.ready()
        clip = self.edl['picture_track'][0]
        clip['semantic_events'][0].update(start_frame=30, end_frame=60)
        for start, end in ((0, 20), (0, 30), (60, 90), (70, 90)):
            with self.subTest(start=start, end=end):
                clip['effect_cues'][0].update(start_frame=start, end_frame=end)
                self.write('edit-decision-list.json', self.edl)
                self.assertTrue(any('帧范围不相交' in error for error in self.errors()))
        for start, end in ((0, 31), (30, 60), (59, 90), (0, 90)):
            with self.subTest(start=start, end=end):
                clip['effect_cues'][0].update(start_frame=start, end_frame=end)
                self.write('edit-decision-list.json', self.edl)
                self.assertEqual(self.errors(), [])

    def test_every_bound_instance_must_overlap_and_lead_in_can_expand_event(self):
        _, event = self.effect()
        direction = self.data['shots'][0]['direction']
        second = copy.deepcopy(direction['effects'][0])
        second['instance_id'] = 'fade-second'
        direction['effects'].append(second)
        event['effect_instance_ids'].append('fade-second')
        self.ready()
        clip = self.edl['picture_track'][0]
        clip['semantic_events'][0].update(start_frame=30, end_frame=60)
        clip['effect_cues'][0].update(start_frame=30, end_frame=60)
        clip['effect_cues'][1].update(start_frame=0, end_frame=20)
        self.write('edit-decision-list.json', self.edl)
        self.assertTrue(any('fade-second' in error and '帧范围不相交' in error
                            for error in self.errors()))
        clip['semantic_events'][0]['start_frame'] = 0
        self.write('edit-decision-list.json', self.edl)
        self.assertEqual(self.errors(), [])

    def test_music_continuation_cannot_restart_or_fade_at_internal_cut(self):
        self.audio()
        self.music(0,after=True)
        self.music(1,before=True)
        self.ready()
        self.assertEqual(self.errors(),[])
        self.edl['picture_track'][1]['music_cue']['source_start_frame']=0
        self.write('edit-decision-list.json',self.edl)
        self.assertTrue(any('源位置不连续' in e for e in self.errors()))
        self.edl['picture_track'][1]['music_cue']['source_start_frame']=90
        self.data['shots'][1]['direction']['music']['fade_in_ms']=100
        self.edl['picture_track'][1]['music_cue']['fade_in_ms']=100
        self.write('edit-decision-list.json',self.edl)
        self.assertTrue(any('内部边界' in e for e in self.errors()))

    def test_music_duration_and_unreciprocated_continuation_rejected(self):
        self.audio()
        self.music(0,after=True)
        self.assertTrue(any('双向' in e for e in self.errors()))
        self.music(1,before=True)
        self.ready()
        self.edl['picture_track'][1]['music_cue']['source_start_frame']=9999
        self.write('edit-decision-list.json',self.edl)
        self.assertTrue(any('音频长度' in e for e in self.errors()))

    def test_ambience_tail_has_contiguous_asset_and_source_frames(self):
        self.audio()
        for index in (0,1):
            _,event=self.effect(index)
            self.request(index)
            event['sound']={'mode':'ambience','reason':'保持场景连贯','request_id':'audio-request','start_trigger':'场景开始',
                            'stop_trigger':'场景结束','continuity':{'from_previous':index==1,'to_next':index==0}}
        self.ready()
        self.assertEqual(self.errors(),[])
        cue=self.edl['picture_track'][1]['semantic_events'][0]['sound']
        cue['source_start_frame']=0
        self.write('edit-decision-list.json',self.edl)
        self.assertTrue(any('跨镜声音的源位置' in e for e in self.errors()))
        cue['source_start_frame']=90
        cue['fade_in_ms']=50
        self.write('edit-decision-list.json',self.edl)
        self.assertTrue(any('再次淡入' in e for e in self.errors()))

    def test_source_action_can_plan_a_missing_video_without_inventing_effect(self):
        request=fixtures.asset_request('footage','实拍视频')
        direction=self.data['shots'][0]['direction']
        direction['assets_needed']=[request]
        event=fixtures.event('native-action','交任务')
        event.update(kind='source-action',source_request_id='footage',effect_instance_ids=[])
        direction['events']=[event]
        self.assertEqual(self.errors(),[])
        self.assertIn('源素材已有动作',render_board(self.project))
        self.ready()
        self.assertTrue(any('视频' in e or '素材' in e for e in self.errors()))

    def test_source_action_ready_needs_video_and_review_bound_to_asset(self):
        self.test_source_action_can_plan_a_missing_video_without_inventing_effect()
        item=self.audio('footage')
        self.data['shots'][0]['direction']['assets_needed'][0]['selected_asset_ids']=['footage']
        proof={'event_id':'native-action','asset_sha256':item['sha256'],'status':'reviewed','reviewer':'测试审阅人','details':'人物递交任务纸张'}
        self.write('action-review.json',proof)
        source={'asset_id':'footage','source_start_frame':10,'source_end_frame':40,'evidence_path':'action-review.json','evidence_sha256':fixtures.digest(self.project/'action-review.json')}
        self.edl['picture_track'][0]['semantic_events'][0]['source_action']=source
        self.write('edit-decision-list.json',self.edl)
        self.assertTrue(any('真实且有时长的视频' in e for e in self.errors()))
        # 隔离视频探测边界；此测试不生成影片。真实 WAV 不能冒充视频的路径已在上面测试。
        with mock.patch('director_plan_resources.media_info',return_value={'duration':12}):
            self.assertEqual(self.errors(),[])
            source['source_end_frame']=999
            self.write('edit-decision-list.json',self.edl)
            self.assertTrue(any('源视频' in e for e in self.errors()))
            source['source_end_frame']=40
            proof['asset_sha256']='0'*64
            self.write('action-review.json',proof)
            source['evidence_sha256']=fixtures.digest(self.project/'action-review.json')
            self.write('edit-decision-list.json',self.edl)
            self.assertTrue(any('素材版本' in e for e in self.errors()))

    def test_export_contains_background_music_and_only_edl_measured_cues(self):
        self.effect(target='background')
        self.audio()
        self.music()
        self.ready()
        board=render_board(self.project,True)
        for expected in ('背景：已有动效','许可 MIT','旁白避让','源起点 0 帧','本镜 0–90 帧','实测 0.000–3.000'):
            self.assertIn(expected,board)
        self.assertNotIn('预计总时长',board)

    def test_malformed_new_fields_fail_without_crashing(self):
        baseline=copy.deepcopy(self.data)
        cases=[lambda d:d['director_plan'].update(effect_catalog=None),
               lambda d:d['shots'][0]['direction'].update(background=[]),
               lambda d:d['shots'][0]['direction'].update(music={'mode':[]}),
               lambda d:d['shots'][0]['direction'].update(effects=[None]),
               lambda d:d['shots'][0]['direction'].update(estimated_duration_seconds=10**1000)]
        for change in cases:
            with self.subTest(change=change):
                self.fixture.data=self.data=copy.deepcopy(baseline)
                change(self.data)
                self.assertTrue(self.errors())

    def test_audio_probe_rejects_invalid_json_shapes_and_text_disguised_as_ogg(self):
        path=self.project/'fake.ogg'
        path.write_text('not media')
        self.assertIsNone(media_info(path,'audio'))
        for value in ('[]','{"streams":null}','{"streams":[{"codec_type":"audio"}],"format":[]}'):
            with mock.patch('director_plan_resources.shutil.which',return_value='/example/ffprobe'), mock.patch('director_plan_resources.subprocess.run',return_value=mock.Mock(returncode=0,stdout=value)):
                self.assertIsNone(media_info(path,'audio'))


def render_board_for_valid_effect(case):
    case.effect(target='background')
    return render_board(case.project)


if __name__ == '__main__':
    unittest.main()
