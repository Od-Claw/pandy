# GitHub Pages Checklist

- [x] `index.html` exists.
- [x] `admin.html` exists.
- [x] `.nojekyll` exists.
- [x] `assets/images/deities` contains the 10 required deity PNG files.
- [x] `assets/images/offerings` contains the 7 required offering PNG files.
- [x] `assets/images/symbols` contains the 8 required auspicious symbol PNG files.
- [x] `assets/audio/buddha-music` exists.
- [x] `assets/audio/buddha-music/music_manifest.json` exists.
- [x] Runtime asset paths are relative paths.
- [x] `index.html` and `admin.html` do not contain `D:\` absolute paths.
- [x] `index.html` and `admin.html` do not hard-code localhost, `127.0.0.1`, or `192.168.*`.
- [x] `index.html` does not depend on `/api` to display sponsor labels.
- [x] `admin.html` uses localStorage in GitHub Pages static mode.
- [x] GitHub Pages static mode can open locally with `python -m http.server`.
- [x] Admin localStorage fallback can update sponsor names for the same browser.

Notes:

- README files include localhost examples for local preview; this is documentation only.
- GitHub Pages cannot write JSON back to the repository. Use import/export JSON or connect a real backend if shared storage is required.
