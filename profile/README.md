# Open OTT Play

Open-source IPTV/OTT playback for set-top boxes, smart TVs, and the browser.
FOSS revival of a classic STB web player — TypeScript sources, one ES5 classic
bundle (`dist/stbPlayer.js`), still runnable on MAG / Dune / Tizen-era engines.

## Projects

### [ottplay-foss](https://github.com/open-ott-play/ottplay-foss)

The main project: browser IPTV/OTT player for 24 device families (Samsung Tizen,
LG webOS, Panasonic Viera, Infomir MAG, Dune HD, Android TV, desktop, and more),
plus a local Rust HTTP(S) server for static files, EPG, M3U matching, stream
proxy, and TMDB.

- **Playback** — HLS, DASH, and plain HTTP via hls.js and Shaka Player
- **EPG** — XMLTV with fuzzy channel matching, timeshift / archive
- **Providers** — M3U, Xtream Codes, Stalker middleware
- **Server** — Rust `ottplay-server` (axum): EPG cache, match-channels, CORS stream proxy, optional TLS on `:8443`
- **Docker** — multi-arch images on [Docker Hub](https://hub.docker.com/r/alvit/ottplay-foss) (`latest`, semver, `sha-*`)
- **Push commands** — local command queue for Home Assistant / Node-RED (central webhook poll stays disabled)
- **UI** — ES5-safe chrome (OSD / lists / OSK), 21 languages, parental, favorites

```bash
git clone https://github.com/open-ott-play/ottplay-foss.git
cd ottplay-foss
npm install && npm run build
```

### [ottplay-swop](https://github.com/open-ott-play/ottplay-swop)

Cloudflare Worker for one-time session handoff (phone types text for the TV when
they are on different networks). TV/desktop calls are gated by an **allowlisted
Device UUID** — public FOSS installs cannot use our KV without an operator
allowlist entry.

- Repo: https://github.com/open-ott-play/ottplay-swop
- Access control: https://github.com/open-ott-play/ottplay-swop#access-control
- Player side: see ottplay-foss README (Remote text entry / swop)
