import pytest
import uuid
from app.realtime.asr.session import AsrSession
from app.realtime.asr.service import AsrService
from app.realtime.asr.types import TranscriptType, TranscriptEvent
from app.realtime.vad.types import VadEvent, VadEventType

class MockScheduler:
    def __init__(self):
        self.jobs = []
        self._sequence = iter(range(1000))
    async def submit(self, job):
        self.jobs.append(job)

@pytest.fixture
def asr_service():
    srv = AsrService()
    srv.scheduler = MockScheduler()
    srv.enabled = True
    return srv

@pytest.fixture
def session(asr_service):
    conn_id = str(uuid.uuid4())
    sess = AsrSession(
        connection_id=conn_id,
        input_sample_rate=8000,
        sample_rate=16000,
        pre_roll_ms=500
    )
    asr_service.sessions[conn_id] = sess
    return sess

@pytest.mark.asyncio
async def test_1_confirmed_bug(asr_service, session):
    # A starts
    await asr_service.handle_vad_event(
        session.connection_id, None,
        VadEvent(created_ns=0, event_type=VadEventType.SPEECH_START, sample_index=0, probability=1.0, detection_delay_ms=0)
    )
    utt_a = session.active_utterance_id
    assert utt_a is not None

    # PENDING_END(A)
    await asr_service.handle_vad_event(
        session.connection_id, None,
        VadEvent(created_ns=0, event_type=VadEventType.SPEECH_PENDING_END, sample_index=16000, probability=0.0, detection_delay_ms=512)
    )
    assert session.get_utterance(utt_a).tentative_inflight == True
    
    # SPEECH_END(A)
    await asr_service.handle_vad_event(
        session.connection_id, None,
        VadEvent(created_ns=0, event_type=VadEventType.SPEECH_END, sample_index=16000, probability=0.0, detection_delay_ms=512)
    )
    assert session.get_utterance(utt_a).finalized == True

    # B starts naturally
    await asr_service.handle_vad_event(
        session.connection_id, None,
        VadEvent(created_ns=0, event_type=VadEventType.SPEECH_START, sample_index=32000, probability=1.0, detection_delay_ms=0)
    )
    utt_b = session.active_utterance_id
    assert utt_b != utt_a

    # FINAL_TENTATIVE(A) arrives
    event = TranscriptEvent.create(
        connection_id=session.connection_id,
        session_uuid=None,
        utterance_id=utt_a,
        transcript_type=TranscriptType.FINAL_TENTATIVE,
        raw_text="My name is Daniel Smith",
        normalized_text="My name is Daniel Smith",
        revision=session.get_utterance(utt_a).revision,
        audio_duration_ms=1000,
        decode_ms=500,
        queue_wait_ms=0
    )
    # The interceptor or service might handle it
    await asr_service.handle_transcript(event)
    
    # Assert A is promoted directly to FINAL (because it was finalized)
    assert event.transcript_type == TranscriptType.FINAL
    assert session.get_utterance(utt_a).final_emitted == True
    
    # And B is unaffected
    assert session.active_utterance_id == utt_b

@pytest.mark.asyncio
async def test_2_same_utterance_resumes(asr_service, session):
    # A starts
    await asr_service.handle_vad_event(
        session.connection_id, None,
        VadEvent(created_ns=0, event_type=VadEventType.SPEECH_START, sample_index=0, probability=1.0, detection_delay_ms=0)
    )
    utt_a = session.active_utterance_id
    
    # PENDING_END(A)
    await asr_service.handle_vad_event(
        session.connection_id, None,
        VadEvent(created_ns=0, event_type=VadEventType.SPEECH_PENDING_END, sample_index=16000, probability=0.0, detection_delay_ms=512)
    )
    old_rev = session.get_utterance(utt_a).revision
    
    # RESUMED(A)
    await asr_service.handle_vad_event(
        session.connection_id, None,
        VadEvent(created_ns=0, event_type=VadEventType.SPEECH_RESUMED, sample_index=24000, probability=1.0, detection_delay_ms=0)
    )
    assert session.get_utterance(utt_a).revision > old_rev
    
    # tentative completes for old revision
    event = TranscriptEvent.create(
        connection_id=session.connection_id,
        session_uuid=None,
        utterance_id=utt_a,
        transcript_type=TranscriptType.FINAL_TENTATIVE,
        raw_text="My name is Daniel",
        normalized_text="My name is Daniel",
        revision=old_rev,
        audio_duration_ms=1000,
        decode_ms=500,
        queue_wait_ms=0
    )
    await asr_service.handle_transcript(event)
    
    # Should be discarded (not promoted to FINAL, not marked as tentative_result)
    assert session.get_utterance(utt_a).tentative_result is None
    assert session.get_utterance(utt_a).final_emitted == False

@pytest.mark.asyncio
async def test_3_next_starts_before_asr_completes(asr_service, session):
    await asr_service.handle_vad_event(
        session.connection_id, None,
        VadEvent(created_ns=0, event_type=VadEventType.SPEECH_START, sample_index=0, probability=1.0, detection_delay_ms=0)
    )
    utt_a = session.active_utterance_id
    await asr_service.handle_vad_event(
        session.connection_id, None,
        VadEvent(created_ns=0, event_type=VadEventType.SPEECH_END, sample_index=16000, probability=0.0, detection_delay_ms=512)
    )
    
    # B starts
    await asr_service.handle_vad_event(
        session.connection_id, None,
        VadEvent(created_ns=0, event_type=VadEventType.SPEECH_START, sample_index=32000, probability=1.0, detection_delay_ms=0)
    )
    utt_b = session.active_utterance_id
    
    # A completes
    event = TranscriptEvent.create(
        connection_id=session.connection_id,
        session_uuid=None,
        utterance_id=utt_a,
        transcript_type=TranscriptType.FINAL,
        raw_text="Final A",
        normalized_text="Final A",
        revision=session.get_utterance(utt_a).revision,
        audio_duration_ms=1000,
        decode_ms=500,
        queue_wait_ms=0
    )
    await asr_service.handle_transcript(event)
    
    assert session.get_utterance(utt_a).final_emitted == True
    
    # B partial arrives
    event_b = TranscriptEvent.create(
        connection_id=session.connection_id,
        session_uuid=None,
        utterance_id=utt_b,
        transcript_type=TranscriptType.PARTIAL,
        raw_text="Part B",
        normalized_text="Part B",
        revision=session.get_utterance(utt_b).revision,
        audio_duration_ms=1000,
        decode_ms=500,
        queue_wait_ms=0
    )
    await asr_service.handle_transcript(event_b)
    
    assert session.active_utterance_id == utt_b

@pytest.mark.asyncio
async def test_4_duplicate_asr_completion(asr_service, session):
    await asr_service.handle_vad_event(
        session.connection_id, None,
        VadEvent(created_ns=0, event_type=VadEventType.SPEECH_START, sample_index=0, probability=1.0, detection_delay_ms=0)
    )
    utt_a = session.active_utterance_id
    await asr_service.handle_vad_event(
        session.connection_id, None,
        VadEvent(created_ns=0, event_type=VadEventType.SPEECH_END, sample_index=16000, probability=0.0, detection_delay_ms=512)
    )
    
    event1 = TranscriptEvent.create(
        connection_id=session.connection_id,
        session_uuid=None,
        utterance_id=utt_a,
        transcript_type=TranscriptType.FINAL,
        raw_text="Final A",
        normalized_text="Final A",
        revision=session.get_utterance(utt_a).revision,
        audio_duration_ms=1000,
        decode_ms=500,
        queue_wait_ms=0
    )
    await asr_service.handle_transcript(event1)
    
    # Duplicate
    event2 = TranscriptEvent.create(
        connection_id=session.connection_id,
        session_uuid=None,
        utterance_id=utt_a,
        transcript_type=TranscriptType.FINAL,
        raw_text="Final A",
        normalized_text="Final A",
        revision=session.get_utterance(utt_a).revision,
        audio_duration_ms=1000,
        decode_ms=500,
        queue_wait_ms=0
    )
    await asr_service.handle_transcript(event2)
    
    assert session.get_utterance(utt_a).final_emitted == True

@pytest.mark.asyncio
async def test_5_cancelled_tentative(asr_service, session):
    await asr_service.handle_vad_event(
        session.connection_id, None,
        VadEvent(created_ns=0, event_type=VadEventType.SPEECH_START, sample_index=0, probability=1.0, detection_delay_ms=0)
    )
    utt_a = session.active_utterance_id
    
    await asr_service.handle_vad_event(
        session.connection_id, None,
        VadEvent(created_ns=0, event_type=VadEventType.SPEECH_PENDING_END, sample_index=16000, probability=0.0, detection_delay_ms=512)
    )
    old_rev = session.get_utterance(utt_a).revision
    
    # Cancelled explicitly
    session.get_utterance(utt_a).cancelled = True
    
    event = TranscriptEvent.create(
        connection_id=session.connection_id,
        session_uuid=None,
        utterance_id=utt_a,
        transcript_type=TranscriptType.FINAL_TENTATIVE,
        raw_text="Final A",
        normalized_text="Final A",
        revision=old_rev,
        audio_duration_ms=1000,
        decode_ms=500,
        queue_wait_ms=0
    )
    await asr_service.handle_transcript(event)
    
    assert session.get_utterance(utt_a).tentative_result is None

@pytest.mark.asyncio
async def test_6_rapid_natural_turns(asr_service, session):
    turns = ["Hello TalkFlow", "My name is Daniel Smith", "I am 67 years old", "My ZIP code is 7442"]
    
    finals_emitted = []
    
    original_handle = asr_service.handle_transcript
    async def mock_handle(ev):
        was_final = (ev.transcript_type == TranscriptType.FINAL)
        await original_handle(ev)
        if not was_final and ev.transcript_type == TranscriptType.FINAL:
            if session.get_utterance(ev.utterance_id).final_emitted:
                finals_emitted.append(ev.text)
                
    asr_service.handle_transcript = mock_handle
    
    for i, text in enumerate(turns):
        await asr_service.handle_vad_event(
            session.connection_id, None,
            VadEvent(created_ns=0, event_type=VadEventType.SPEECH_START, sample_index=i*1000, probability=1.0, detection_delay_ms=0)
        )
        utt = session.active_utterance_id
        
        await asr_service.handle_vad_event(
            session.connection_id, None,
            VadEvent(created_ns=0, event_type=VadEventType.SPEECH_PENDING_END, sample_index=i*1000+500, probability=0.0, detection_delay_ms=512)
        )
        await asr_service.handle_vad_event(
            session.connection_id, None,
            VadEvent(created_ns=0, event_type=VadEventType.SPEECH_END, sample_index=i*1000+500, probability=0.0, detection_delay_ms=512)
        )
        
        event = TranscriptEvent.create(
            connection_id=session.connection_id,
            session_uuid=None,
            utterance_id=utt,
            transcript_type=TranscriptType.FINAL_TENTATIVE,
            raw_text=text,
            normalized_text=text,
            revision=session.get_utterance(utt).revision,
            audio_duration_ms=1000,
            decode_ms=500,
            queue_wait_ms=0
        )
        await asr_service.handle_transcript(event)
    
    # We expect 4 distinct finals emitted
    assert len(finals_emitted) == 4
    assert finals_emitted == turns
