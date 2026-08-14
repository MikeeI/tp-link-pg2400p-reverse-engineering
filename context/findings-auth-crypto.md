# Authentication and cryptography

## Confirmed client contract

- [confirmed] `modules/login/localLogin/controllers.js` computes `md5(password)` before login.
- [confirmed] `modules/login/localLogin/models.js` sends the resulting digest in `TPLINK.GENERAL.LOGIN_PASSWORD` through the `MERProxyNew` write path.
- [confirmed] `MERProxyNew` sends that login as `POST /` with form encoding.
- [confirmed] The successful browser request shape was a same-origin form POST with `Origin`, `Referer`, `X-Requested-With: XMLHttpRequest`, browser `Accept`/`Accept-Encoding`, and the MD5 field body.
- [confirmed] The browser login response on both owned devices was HTTP 200 and matched `ERROR=000` followed by a `TOKEN` field; token bytes are deliberately absent from curated evidence.
- [confirmed] `main.js` stores the token in browser `localStorage`, copies it to `$.su.url.session`, and `url.js` appends it as `_t=<URL-encoded token>` to subsequent API URLs.
- [confirmed] `main.js` also stores the MD5 digest in browser local storage under `lgkey`; this is browser-local behavior, not evidence of device-side credential storage.
- [confirmed] `.185` authenticated browser session completed `COMMAND=logout` with HTTP 200 and `ERROR=000`, then cleared browser local/session storage.

## Response handling

- [confirmed] The static parser splits text on CRLF and maps every non-`ERROR` `KEY=VALUE` line to a field.
- [confirmed] Client constants identify application error 4 as `ETOKEN`.
- [confirmed] An unauthenticated `.185` identity request returned `ERROR=004`; an authenticated request returned `ERROR=000`.

## Direct-curl discrepancy

- [confirmed] After preflight capture, a minimal direct `.184` form POST received HTTP 401.
- [confirmed] One browser-header-shaped retry received HTTP 405.
- [confirmed] The browser implementation immediately succeeded against `.184` and `.185` with the same MD5 field contract and created usable `_t` sessions.
- [likely] The direct-curl failures reflect request-shape or transient server/request-state differences, not invalid credentials or a device lockout.
- [confirmed] No further direct login attempt was made after the authorized retry.

## Security boundary observations

- [confirmed] Management and credentials traverse plain HTTP on the observed port-80 service.
- [confirmed] The observed root and login-failure response headers contain no `Set-Cookie` or `WWW-Authenticate` header.
- [likely] `_t` is the complete session bearer for this web client because client code appends it to API URLs and uses local storage rather than cookies; handler-side token validation remains runtime-only evidence.

## Action status

- `NOW`: use browser-proven form encoding, parse `ERROR` first, retain tokens only in-process, and send the known logout command during cleanup.
- `RUNTIME-NEEDED`: capture session expiration, token scope, concurrency, and invalid-token behavior without retries that risk lockout.
- `BLOCKED`: no password changes, recovery flow, or credential-storage conclusions are authorized from this evidence.

## Provenance

Static source bytes and the successful `.184` browser trace are bound by hashes in `data/extracted-live/extracted-knowledge/live-web-evidence.txt`.
