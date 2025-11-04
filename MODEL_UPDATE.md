# Model Name Update - claude-sonnet-4-5

## Summary

Updated all references to Claude model from `claude-sonnet-4-20250514` to the correct model name `claude-sonnet-4-5`.

## Files Modified

| File | Line | Old Value | New Value |
|------|------|-----------|-----------|
| `tmi_tf/claude_analyzer.py` | 50 | `"claude-sonnet-4-20250514"` | `"claude-sonnet-4-5"` |
| `tmi_tf/dfd_llm_generator.py` | 21 | `"claude-sonnet-4-20250514"` | `"claude-sonnet-4-5"` |
| `tmi_tf/cli.py` | 197 | `"claude-sonnet-4-20250514"` | `"claude-sonnet-4-5"` |

## Changes Detail

### 1. tmi_tf/claude_analyzer.py (line 50)
```python
# Before
self.model = "claude-sonnet-4-20250514"  # Claude Sonnet 4.5

# After
self.model = "claude-sonnet-4-5"  # Claude Sonnet 4.5
```

### 2. tmi_tf/dfd_llm_generator.py (line 21)
```python
# Before
def __init__(self, api_key: str, model: str = "claude-sonnet-4-20250514"):

# After
def __init__(self, api_key: str, model: str = "claude-sonnet-4-5"):
```

### 3. tmi_tf/cli.py (line 196-197)
```python
# Before
dfd_generator = DFDLLMGenerator(
    api_key=config.anthropic_api_key,
    model="claude-sonnet-4-20250514"
)

# After
dfd_generator = DFDLLMGenerator(
    api_key=config.anthropic_api_key, model="claude-sonnet-4-5"
)
```

## Verification

- ✅ All Python files updated
- ✅ No references to old model name in documentation
- ✅ Linting passed (ruff)
- ✅ Formatting applied (black)
- ✅ Import test successful
- ✅ No breaking changes

## Impact

**None** - This is a drop-in replacement. The model name is the only change, and both model names refer to Claude Sonnet 4.5. The API will accept both model IDs for now, but `claude-sonnet-4-5` is the canonical name.

## Testing

Existing functionality remains unchanged. All API calls will use the updated model name going forward.

To test:
```bash
# Verify imports work
uv run python -c "from tmi_tf.claude_analyzer import ClaudeAnalyzer; print('✓ OK')"

# Run full analysis (requires valid config)
uv run tmi-tf analyze <threat-model-id>
```

## Notes

The model name `claude-sonnet-4-5` is the canonical identifier for Claude Sonnet 4.5. While the dated identifier `claude-sonnet-4-20250514` may still work, using the canonical name ensures compatibility with future API updates.
