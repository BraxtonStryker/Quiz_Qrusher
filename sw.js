/* Quiz Qrusher service worker (v3.0, Phase 8). Keeps the app working offline once it has been opened.
 *
 * - Every file in PRECACHE is cached together under one version; requests for them are answered from that cache.
 * - VERSION is a hash of those files' contents, written by `python -I test-data/harness/check_shared.py --sync`.
 *   When any of them changes, VERSION changes, so this file changes and browsers install the new version.
 * - A new version waits until the page asks it to take over (the "New version available" toast's Reload),
 *   so an open quiz is never swapped out from under the user.
 * - Only same-origin GETs inside this scope are touched. Everything else (e.g. the Google Form) goes to the network.
 * - Cache names start with "quizQrusher-": every GitHub Pages project of this user shares the origin.
 */
"use strict";
const VERSION = "4e458b8587e9"; // generated: check_shared.py --sync
const CACHE = "quizQrusher-" + VERSION;
const PRECACHE = [
  "./",
  "index.html",
  "lite.html",
  "manifest.webmanifest",
  "icons/icon.svg",
  "icons/icon-192.png",
  "icons/icon-512.png",
  "icons/icon-maskable-512.png",
  "icons/apple-touch-icon.png",
  "prompts/medical/medical_prompts.zip"
];

self.addEventListener("install", (event) => {
  event.waitUntil(caches.open(CACHE).then((c) => c.addAll(PRECACHE.map((u) => new Request(u, { cache: "reload" })))));
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k.indexOf("quizQrusher-") === 0 && k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("message", (event) => {
  if (event.data && event.data.type === "SKIP_WAITING") self.skipWaiting();
});

self.addEventListener("fetch", (event) => {
  const req = event.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);
  if (url.origin !== self.location.origin || !url.href.startsWith(self.registration.scope)) return;
  const precached = PRECACHE.some((p) => new URL(p, self.registration.scope).href === url.origin + url.pathname);
  if (!precached && req.mode !== "navigate") return;      // anything else: straight to the network
  event.respondWith(
    caches.open(CACHE).then((c) => c.match(req, { ignoreSearch: true })).then((hit) => hit || fetch(req))
  );
});
