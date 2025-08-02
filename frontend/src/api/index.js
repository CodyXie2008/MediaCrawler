export async function getConfig() {
  return fetch('/api/config').then(res => res.json());
}
export async function saveConfig(data) {
  return fetch('/api/config', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data)});
}
export async function startCrawler(params) {
  return fetch('/api/crawler/start', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(params)});
}
export async function stopCrawler() {
  return fetch('/api/crawler/stop', {method: 'POST'});
}
export async function getStatus() {
  return fetch('/api/crawler/status').then(res => res.json());
}
export async function getLogs() {
  return fetch('/api/crawler/logs').then(res => res.json());
} 