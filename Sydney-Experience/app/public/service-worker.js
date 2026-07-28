const CACHE_NAME = "moon-window-v6";
const APP_SHELL = [
  "/",
  "/styles.css",
  "/app.js",
  "/manifest.json",
  "/assets/moonmark.svg",
  "/assets/moon-window-rain-calm-v2.webp",
  "/assets/moon-window-rain-attentive-v2.webp",
  "/assets/moon-window-rain-joy-v2.webp",
  "/assets/moon-window-rain-vulnerable-v2.webp",
  "/assets/moon-window-rain-intimate-v2.webp",
  "/content/prologue.json",
  "/content/story.schema.json",
  "/content/scenes.json"
];

self.addEventListener("install", (event) => {
  event.waitUntil(caches.open(CACHE_NAME).then((cache) => cache.addAll(APP_SHELL)));
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key)))
    )
  );
  self.clients.claim();
});

self.addEventListener("fetch", (event) => {
  if (event.request.method !== "GET" || new URL(event.request.url).pathname.startsWith("/api/")) return;
  event.respondWith(
    fetch(event.request)
      .then((response) => {
        const copy = response.clone();
        caches.open(CACHE_NAME).then((cache) => cache.put(event.request, copy));
        return response;
      })
      .catch(async () => {
        const cached = await caches.match(event.request);
        if (cached) return cached;
        if (event.request.mode === "navigate") return caches.match("/");
        return new Response("Offline", { status: 504, statusText: "Offline" });
      })
  );
});
