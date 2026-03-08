# Crafted Daily Financial Report Setup

## Google Drive Integration (Read-Only)

### Service Account Setup Required

1. Create Google Cloud Project
2. Enable Google Drive API
3. Create service account
4. Download credentials JSON
5. Share document with service account email

### Test Document
- URL: https://docs.google.com/spreadsheets/d/1u7Du_KjwGvEL-Jp0oI91Zjlq8gYtxOx5/edit?usp=drivesdk&ouid=101241787498200223121&rtpof=true&sd=true

### Required Scope
- `https://www.googleapis.com/auth/drive.readonly`

### Daily Report Schedule
- Time: 11:00 PM WITA (Bali time)
- Data sources: Google Drive (expenses), Mokapos (revenue)
- Output: Summary report to Telegram

## Notes
- Awaiting Mokapos credentials from Tony
- Google Drive access: Pending service account creation
