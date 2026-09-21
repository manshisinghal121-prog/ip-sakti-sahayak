/* IP-SAKTI Sahayak authentication helper */
(function () {
  const TOKEN_KEY = "ipSaktiAccessToken";
  const USER_KEY = "ipSaktiUsername";

  function apiBase() {
    return window.location.protocol === "file:" ? "http://127.0.0.1:8000" : window.location.origin;
  }

  function getAuthToken() { return localStorage.getItem(TOKEN_KEY); }
  function getAuthUser() { return localStorage.getItem(USER_KEY); }
  function setAuth(token, username) {
    localStorage.setItem(TOKEN_KEY, token);
    if (username) localStorage.setItem(USER_KEY, username);
  }
  function clearAuth() {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
  }

  function loginUrl() {
    const next = encodeURIComponent(window.location.pathname + window.location.search);
    return `/login?next=${next}`;
  }

  async function authFetch(url, options = {}) {
    const headers = new Headers(options.headers || {});
    const token = getAuthToken();
    if (token) headers.set("Authorization", `Bearer ${token}`);
    if (options.body && !headers.has("Content-Type")) headers.set("Content-Type", "application/json");

    const response = await fetch(url, {...options, headers});
    if (response.status === 401) {
      clearAuth();
      window.location.href = loginUrl();
    }
    return response;
  }

  window.IPSAKTI_AUTH = { TOKEN_KEY, USER_KEY, apiBase, getAuthToken, getAuthUser, setAuth, clearAuth, authFetch };
  window.getAuthToken = getAuthToken;
  window.authFetch = authFetch;
  window.logoutIPSAKTI = function () { clearAuth(); window.location.href = "/login"; };

  // Protected assistant workspace: unauthenticated visitors go to the real login page.
  if (window.location.pathname === "/assistant" && !getAuthToken()) {
    window.location.replace(loginUrl());
  }
})();
