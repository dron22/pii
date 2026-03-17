# pii — Safe AI Document Preparation

## The Problem
Every day, people share sensitive documents — pension statements, insurance forms,
tax returns — with AI tools and cloud services. The moment you upload, your name,
address, tax ID, and IBAN are out of your hands.

There is no safe way to use AI on private documents today.

## The Solution
**pii** is a local tool that detects and blacks out personal information before
you share anything. A password-protected key file lets you restore the original
values at any time. No data ever leaves your device.

## How It Works
1. Upload a PDF (or run `pii redact document.pdf`)
2. Review the detected PII fields — the tool shows what it found before acting
3. Download the redacted PDF (safe to share with any AI or service)
4. Keep the encrypted key file — restore originals anytime with your password

## Reversibility
Each redacted field is replaced by a typed token: `[NAME_1]`, `[IBAN_1]`, etc.
The key file maps every token back to its original value, encrypted with
AES-256-GCM. Only you can unlock it.

## Technical Stack
| Component          | Technology                                      |
|--------------------|-------------------------------------------------|
| PII detection      | Microsoft Presidio + spaCy NER                  |
| Custom recognisers | AHV/AVS, IBAN, insurance numbers, patient IDs   |
| PDF manipulation   | PyMuPDF                                         |
| Key encryption     | AES-256-GCM (Python cryptography library)       |
| Web UI             | Gradio                                          |
| Execution          | 100% local — no cloud, no server                |

## Detected PII Types
Full name · Date of birth · AHV / AVS number · IBAN · Phone · Email ·
Patient ID · Insurance number · National / passport ID · Street address ·
Diagnosis codes (opt-in)

## Privacy Design
- All processing happens on your machine — nothing is transmitted
- The key file is encrypted; without the password it is unreadable
- The tool shows what it will redact before making any changes
- Open source — auditable by anyone

## Limitations
- Text-based PDFs only (scanned document support planned)
- Primary language: English (Swiss-specific identifiers fully supported)

## Repository
[https://github.com/dron22/pii](https://github.com/dron22/pii)
