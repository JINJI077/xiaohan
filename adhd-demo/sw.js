const CACHE_NAME = "adhd-launcher-v36";
const ASSETS = [
  "./",
  "./index.html",
  "./styles.css?v=33",
  "./app.js?v=33",
  "./manifest.webmanifest",
  "./icon.svg",
  "./图片素材/花园.png",
  "./图片素材/小草-没花.png",
  "./图片素材/小草-有花版本.png",
];

self.addEventListener("install", (event) => {
  event.waitUntil(caches.open(CACHE_NAME).then((cache) => cache.addAll(ASSETS)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches
      .keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k))))
      .then(() => self.clients.claim()),
  );
});

self.addEventListener("fetch", (event) => {
  const req = event.request;
  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return;

  if (req.mode === "navigate") {
    event.respondWith(caches.match(req).then((hit) => hit || caches.match("./") || caches.match("./index.html")));
    return;
  }

  event.respondWith(
    caches.match(req).then(
      (hit) =>
        hit ||
        fetch(req)
          .then((res) => {
            const copy = res.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(req, copy));
            return res;
          })
          .catch(() => caches.match(req)),
    ),
  );
});
