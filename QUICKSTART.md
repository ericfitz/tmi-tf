# Quick Start Guide

Get started with the TMI Terraform Analysis Tool in minutes.

## Step 1: Install Dependencies

```bash
cd ~/Projects/tmi-tf
uv sync
```

## Step 2: Configure API Keys

Edit `.env` and add your Anthropic API key:

```bash
# Required
ANTHROPIC_API_KEY=sk-ant-xxx...

# Optional (for higher GitHub rate limits)
GITHUB_TOKEN=ghp_xxx...
```

## Step 3: Test Configuration

```bash
uv run tmi-tf config-info
```

You should see your configuration displayed (without showing actual API keys).

## Step 4: Authenticate with TMI

```bash
uv run tmi-tf auth
```

This will:
1. Open your browser to Google Sign-In
2. Authenticate with TMI server
3. Cache your token for future use

## Step 5: Find Your Threat Model ID

In the TMI web interface:
1. Navigate to your threat model
2. Copy the UUID from the URL (e.g., `abc-123-def-456`)

Or list threat models via TMI API (requires manual API call for now).

## Step 6: List Repositories

View repositories in your threat model:

```bash
uv run tmi-tf list-repos <your-threat-model-id>
```

This shows which repositories will be analyzed.

## Step 7: Run Analysis

### Dry Run (No Note Creation)

Test the analysis without creating a note:

```bash
uv run tmi-tf analyze <your-threat-model-id> --dry-run
```

### Full Analysis

Analyze and create note in TMI:

```bash
uv run tmi-tf analyze <your-threat-model-id>
```

### Save to File

Save markdown report to a file:

```bash
uv run tmi-tf analyze <your-threat-model-id> --output report.md
```

## Common Options

```bash
# Verbose logging
uv run tmi-tf analyze <id> --verbose

# Analyze only 1 repository
uv run tmi-tf analyze <id> --max-repos 1

# Force re-authentication
uv run tmi-tf analyze <id> --force-auth

# Combine options
uv run tmi-tf analyze <id> --max-repos 1 --dry-run --verbose
```

## Troubleshooting

### "ANTHROPIC_API_KEY not configured"

Edit `.env` and set your actual Anthropic API key (replace the placeholder).

### "Failed to get authorization URL"

Check that:
- TMI server is accessible: https://api.tmi.dev
- You have internet connection
- No firewall blocking the connection

### "No GitHub repositories found"

Your threat model may not have any GitHub repositories with Terraform code.
Use `list-repos` to see what repositories are available.

### Rate Limits

If you hit GitHub rate limits (60/hour unauthenticated):
- Add `GITHUB_TOKEN` to `.env`
- Or reduce `--max-repos`

## What to Expect

When you run analysis:

1. **Authentication** (~5-10 seconds if cached, ~30 seconds if new)
2. **Threat Model Fetch** (~1-2 seconds)
3. **Repository Discovery** (~2-5 seconds)
4. **Cloning** (~10-60 seconds per repo, depends on size)
5. **AI Analysis** (~30-120 seconds per repo with Claude)
6. **Report Generation** (~1-2 seconds)
7. **Note Creation** (~2-5 seconds)

Total time for 3 small-medium repos: **2-10 minutes**

## Next Steps

After analysis completes:

1. Check the TMI threat model for the new note
2. Review the analysis findings
3. Use the mermaid diagrams to visualize architecture
4. Start threat modeling based on identified components and flows

## Tips

- Start with `--max-repos 1` to test on a single repository
- Use `--dry-run` to preview before creating notes
- Save outputs to files with `--output` for offline review
- Enable `--verbose` if you encounter issues
- Clear auth cache with `clear-auth` if having token issues

## Example Workflow

```bash
# 1. Check configuration
uv run tmi-tf config-info

# 2. Authenticate
uv run tmi-tf auth

# 3. List repositories to verify
uv run tmi-tf list-repos abc-123-def

# 4. Test with one repo
uv run tmi-tf analyze abc-123-def --max-repos 1 --dry-run --verbose

# 5. Full analysis when ready
uv run tmi-tf analyze abc-123-def --output analysis.md

# 6. Review the note in TMI web interface
```

---

Need help? Check the full [README.md](README.md) for detailed documentation.
