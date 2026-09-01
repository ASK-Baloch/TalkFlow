import re

with open('tests/unit/qualification/test_engine.py', 'r') as f:
    content = f.read()

# Fix test_complete_qualified_flow
content = re.sub(
    r'    result = engine\.process_transcript\(\s*session=session,\s*text=\"Yes, I have Part A\.\",\s*\)\s*assert result\.action\.action_type == ActionType\.ASK_PART_B\s*result = engine\.process_transcript\(\s*session=session,\s*text=\"Yes, I have Part B\.\",\s*\)\s*assert result\.action\.action_type == ActionType\.ASK_ZIP',
    '    result = engine.process_transcript(\n        session=session,\n        text="Yes, I have Part A.",\n    )\n\n    assert result.action.action_type == ActionType.ASK_ZIP',
    content
)

# Fix test_part_a_no_asks_part_b (formerly test_part_a_no_disqualifies)
content = re.sub(
    r'    result = engine\.process_transcript\(\s*session=session,\s*text=\"No, I do not have Part A\.\",\s*\)\s*assert result\.status == QualificationStatus\.DISQUALIFIED\s*assert result\.action\.reason == \"medicare_part_a_missing\"',
    '    result = engine.process_transcript(\n        session=session,\n        text="No, I do not have Part A.",\n    )\n\n    assert result.action.action_type == ActionType.ASK_PART_B',
    content
)

with open('tests/unit/qualification/test_engine.py', 'w') as f:
    f.write(content)
