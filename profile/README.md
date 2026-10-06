# Open OTT Play

Open-source IPTV/OTT software for set-top boxes, smart TVs, Android and browsers.
Players use your own playlists and provider accounts; companion services are
optional and have separate setup and authorization requirements.

## Choose a player

- **[ottplay-foss](https://github.com/open-ott-play/ottplay-foss)** is the browser
  and STB player with platform wrappers and a local Rust HTTP(S) companion.
  Start with its [architecture guide](https://github.com/open-ott-play/ottplay-foss/blob/main/docs/architecture.md)
  and platform installation instructions.
- **[ottplay-android](https://github.com/open-ott-play/ottplay-android)** is the
  independent Kotlin/Compose and Media3 application for Android and Android TV.
  It has a separate application identity and can coexist with the FOSS app.
- **[ottplay-core](https://github.com/open-ott-play/ottplay-core)** owns the shared
  JVM/ES5 domain logic, service wire contracts and the independent
  [FOSS2 browser client](https://github.com/open-ott-play/ottplay-core/tree/main/ottplay-foss2).
  Consumers vendor qualified artifacts and can build without a sibling core checkout.

## Companion services and publication

- **[ottplay-control-server](https://github.com/open-ott-play/ottplay-control-server)**
  delivers remote commands through outbound player requests. It includes a terminal
  remote, portable binaries and a Helm chart. Pairing and administrator access are
  configured separately from playback.
- **[ottplay-swop](https://github.com/open-ott-play/ottplay-swop)** provides optional
  phone-to-player text entry through a Cloudflare Worker. Its current flow authorizes
  an installation through a backend-held credential; per-TV allowlisting is a
  legacy compatibility path. See [installation authorization](https://github.com/open-ott-play/ottplay-swop#installation-authorization).
- **[ottplay-web-vitrine](https://github.com/open-ott-play/ottplay-web-vitrine)**
  publishes reviewed player artifacts and owns the hosted profile and demo assets.
  Try the [browser demo](https://player.ottplay.here.now/). Hosted transports are
  documented in that repository; they need not match a local installation.

## Contribute

Choose the repository that owns the behavior: shared provider/domain rules in
`ottplay-core`, platform UI and device integration in the corresponding player,
and service-specific behavior in its companion repository. Start with that
repository's contributor and validation instructions. Passing portable CI does
not establish compatibility with every physical TV, codec or provider.

This [.github repository](https://github.com/open-ott-play/.github) holds the
organization profile, community files and visual assets. Public GitHub settings
are maintained in [terraform-github-open-ott-play](https://github.com/4alvit/terraform-github-open-ott-play).
