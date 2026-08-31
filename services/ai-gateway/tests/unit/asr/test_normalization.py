from app.realtime.asr.normalization import get_domain_normalizer, normalize_transcript


def test_normalization_positive():
    """
    Test that known phonetic variants are normalized correctly to canonical terms.
    """
    assert normalize_transcript("Hello Talk Low") == "Hello TalkFlow"
    assert normalize_transcript("Hello, Doc Lo.") == "Hello, TalkFlow."
    assert normalize_transcript("Welcome to top flow") == "Welcome to TalkFlow"
    assert normalize_transcript("Welcome to talk flow") == "Welcome to TalkFlow"
    
    assert normalize_transcript("I have Medicare part bee", context_hints=["ASK_PART_B"]) == "I have Medicare Part B"
    assert normalize_transcript("I have Medicare part ay", context_hints=["ASK_PART_A"]) == "I have Medicare Part A"
    assert normalize_transcript("I have Medicaid") == "I have Medicaid"

def test_normalization_negative():
    """
    Test that the normalizer does NOT accidentally corrupt unrelated words.
    """
    # Contains 'top' and 'flow' but not next to each other
    assert normalize_transcript("The top of the pipe has good flow.") == "The top of the pipe has good flow."
    # Contains a partial word match that should NOT be touched (word boundary test)
    assert normalize_transcript("We are stopping flows.") == "We are stopping flows."
    
    # Required negative tests
    assert normalize_transcript("Please talk slow.") == "Please talk slow."
    assert normalize_transcript("The top floor is closed.") == "The top floor is closed."
    assert normalize_transcript("The doctor is running low.") == "The doctor is running low."
    assert normalize_transcript("I saw a bee.") == "I saw a bee."
    assert normalize_transcript("Say the letter A.") == "Say the letter A."
    assert normalize_transcript("The blue crosswalk is ahead.") == "The blue crosswalk is ahead."
    
def test_normalization_with_context():
    """
    Test that context hints properly activate specific state vocabularies.
    """
    normalizer = get_domain_normalizer()
    
    # ASK_PART_A has Medicare_Part_A
    text, corrections = normalizer.normalize("I want Medicare part ay.", context_hints=["ASK_PART_A"])
    assert text == "I want Medicare Part A."
    assert len(corrections) == 1
    assert corrections[0]["corrected"] == "Medicare Part A"

def test_numbers():
    assert normalize_transcript("My zip is seven five zero zero one.") == "My zip is 75001."
