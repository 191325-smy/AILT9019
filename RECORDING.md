# Recording the working core path

Start `start-backend.bat` and `start-frontend.bat` on Windows, then open
http://localhost:8001/index.html. Keep both server windows running.
The scripts use the root `.venv` if it exists, otherwise Python on PATH.
The backend requires Python 3.10+; dependencies are in the root `requirements.txt`.

Register a new username with a password of at least 8 characters. Use synthetic
details: Demo Student, demo@example.com, HK, Frontend, English and Mandarin.
Registration signs in and saves the profile using the real API. The seeded
classmates have placeholder password hashes and cannot be used for login.

Check the saved profile on Dashboard and reload to verify persistence. Run
matching: with the fixture data, expect five same-city candidates, reasons,
filtering statistics and the actual model/fallback source. Edit the profile to
SH and Database, save, and match again: results must change to SH candidates.
Log out and sign in again to verify the saved profile survives.

For the <=60 second MP4, prepare the synthetic account in advance. Show login,
one profile edit and save, the matching button, filter statistics, five
candidates and a reason. Include narration or captions. Clearly identify
deterministic fallback when no live model is used. Time-overlap ranking and
mutual-consent contact sharing are not implemented. All displayed contacts
must remain synthetic.

Local verification on 2026-10-26: 23 backend tests passed, plus an Edge browser
workflow covering registration, persistence, five HK picks, editing to SH,
five SH picks, server-side logout and re-login. This does not validate live
model quality or resolve the earlier evaluation pack's model edge cases.

Real AI matching uses the existing matcher and its `matching/.env` configuration.
For Flash, set `MATCH_MODEL=deepseek:deepseek-flash`, install the root
`requirements.txt` in the shared environment and restart the backend. The final
59-second recording shows this path with the AI Model label.
