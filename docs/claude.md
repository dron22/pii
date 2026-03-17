# Integrating pii with Claude Code

Automatically redact PDFs before Claude reads them — using a Claude Code [PreToolUse hook](https://docs.anthropic.com/en/docs/claude-code/hooks).

Whenever Claude tries to read a `.pdf` file, the hook intercepts the call, runs `pii redact`, and redirects Claude to the redacted copy. The original file is never seen by the model.

## Setup

Add to `~/.claude/settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Read",
        "hooks": [
          {
            "type": "command",
            "command": "PII_PASSWORD=your-password pii claude"
          }
        ]
      }
    ]
  }
}
```

Replace `your-password` with a password of your choice. It encrypts the key files saved next to the original PDFs — you'll need it if you ever want to restore the originals.

## Notes

- Only `.pdf` files are affected — all other file reads pass through unchanged.
- The redacted copy is created once and reused on subsequent reads.
- Key files (`.key.enc`) are saved alongside the original PDF.
- Only text-based PDFs are supported; scanned documents are passed through unchanged.
