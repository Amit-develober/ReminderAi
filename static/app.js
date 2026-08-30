/**
 * PulseAI — Telegram Edition
 * Performance notes:
 *  • Live-preview updates are debounced (150 ms) and scheduled via
 *    requestAnimationFrame so DOM writes only happen on frame boundaries.
 *  • Toast enter/leave animations are CSS-only (transform/opacity),
 *    so the browser compositor handles them — no JS-driven style loops.
 *  • All DOM mutations happen inside rAF callbacks to avoid forced reflows.
 */

document.addEventListener("DOMContentLoaded", () => {
  // ── Element references ─────────────────────────────────────────────────
  const nameInput     = document.getElementById("user-name");
  const chatIdInput   = document.getElementById("user-chat-id");
  const cityInput     = document.getElementById("user-city");
  const subscribeForm = document.getElementById("subscribe-form");
  const btnSubscribe  = document.getElementById("btn-subscribe");
  const btnTestSample = document.getElementById("btn-test-sample");
  const subscriberCountEl = document.getElementById("active-subscriber-count");

  // Live preview DOM
  const prevGreeting = document.getElementById("prev-greeting");
  const prevWeather  = document.getElementById("prev-weather");
  const prevStories  = document.getElementById("prev-stories");

  // ── Topic sample headlines ─────────────────────────────────────────────
  const topicSampleStories = {
    "AI & Machine Learning":    "<strong>• Next-Gen Reasoning Model Released:</strong> Breakthrough benchmarks in multi-step problem solving.",
    "Tech Startups & VC":       "<strong>• VC Funding Shifts to Autonomous AI:</strong> Seed rounds surging for workflow automation agents.",
    "Business & Markets":       "<strong>• Global Markets Rally:</strong> Semiconductor and tech stocks push indexes to fresh record highs.",
    "Crypto & Web3":            "<strong>• Bitcoin & Ethereum Institutional Inflows Surge:</strong> Major ETF products see record weekly trading volume.",
    "Biotech & Science":        "<strong>• AI Accelerates Protein Discovery:</strong> New computational lab synthesizes targeted therapy in days.",
    "Cybersecurity":            "<strong>• Zero-Day Cloud Vulnerability Patched:</strong> Major providers roll out unified fix across global regions.",
    "World News & Geopolitics": "<strong>• International Clean Energy Accord Signed:</strong> Top nations commit to expanded grid modernization.",
    "Gaming & Entertainment":   "<strong>• Next-Gen Engine Revealed:</strong> Real-time neural rendering brings photorealism to mobile devices."
  };

  // ── Debounced rAF preview ─────────────────────────────────────────────
  let previewTimer = null;

  function schedulePreviewUpdate() {
    if (previewTimer) return;           // already scheduled this frame-cycle
    previewTimer = setTimeout(() => {
      requestAnimationFrame(() => {
        doUpdatePreview();
        previewTimer = null;
      });
    }, 150);                            // 150 ms debounce feels instant
  }

  function getSelectedTopics() {
    return [...document.querySelectorAll(".topic-chip.active")]
      .map(chip => chip.dataset.topic);
  }

  function doUpdatePreview() {
    const name   = nameInput.value.trim()   || "Friend";
    const city   = cityInput.value.trim()   || "Your City";
    const topics = getSelectedTopics();

    // Batch all DOM writes together (no interleaved reads)
    prevGreeting.textContent = `Good morning, ${name}! 🚀 Ready to conquer the day?`;
    prevWeather.innerHTML    = `☀️ <strong>Weather in ${city}:</strong> Clear sky, mild morning breeze. Great day ahead!`;

    // Build story list HTML string then set innerHTML once
    let storiesHtml = "";
    if (topics.length === 0) {
      storiesHtml = "<li><strong>• No topics selected:</strong> Tap tags above to customise your pulse.</li>";
    } else {
      topics.slice(0, 3).forEach(t => {
        const html = topicSampleStories[t]
          || `<strong>• ${t} Update:</strong> Key breakthrough shaping industry leaders today.`;
        storiesHtml += `<li>${html}</li>`;
      });
    }
    prevStories.innerHTML = storiesHtml;
  }

  // ── Topic chips ────────────────────────────────────────────────────────
  document.querySelectorAll(".topic-chip").forEach(chip => {
    chip.addEventListener("click", () => {
      chip.classList.toggle("active");
      schedulePreviewUpdate();
    });
  });

  // ── Live input → preview ───────────────────────────────────────────────
  nameInput.addEventListener("input", schedulePreviewUpdate);
  cityInput.addEventListener("input", schedulePreviewUpdate);

  // Run once on load
  doUpdatePreview();

  // ── Toast system ──────────────────────────────────────────────────────
  /**
   * showToast — purely CSS-animated toasts; JS only adds/removes classes.
   * @param {string} message  HTML message text
   * @param {"success"|"error"} type
   * @param {number} durationMs  Auto-dismiss delay in ms (default 4500)
   */
  function showToast(message, type = "success", durationMs = 4500) {
    const container = document.getElementById("toast-container");
    const toast     = document.createElement("div");
    toast.className = `toast ${type}`;

    const icon = type === "success" ? "✅" : "⚠️";
    toast.innerHTML = `
      <span style="font-size:18px;flex-shrink:0">${icon}</span>
      <span>${message}</span>
      <button class="toast-dismiss" aria-label="Dismiss" title="Dismiss">×</button>
    `;

    // Dismiss button
    toast.querySelector(".toast-dismiss").addEventListener("click", () => dismissToast(toast));

    container.appendChild(toast);

    const timerId = setTimeout(() => dismissToast(toast), durationMs);
    toast._timerId = timerId;
  }

  function dismissToast(toast) {
    clearTimeout(toast._timerId);
    toast.classList.add("leaving");
    toast.addEventListener("animationend", () => toast.remove(), { once: true });
    // Fallback removal in case animationend doesn't fire
    setTimeout(() => toast.remove(), 350);
  }

  // ── Subscription form submit ──────────────────────────────────────────
  subscribeForm.addEventListener("submit", async e => {
    e.preventDefault();

    const name   = nameInput.value.trim();
    const chatId = chatIdInput?.value.trim() || "";
    const city   = cityInput.value.trim();
    const topics = getSelectedTopics();

    if (!chatId) {
      showToast("Please enter your Telegram Chat ID.", "error");
      chatIdInput?.focus();
      return;
    }
    if (topics.length === 0) {
      showToast("Please select at least one focus niche.", "error");
      return;
    }

    setButtonLoading(btnSubscribe, true, `<span class="spinner"></span><span>Subscribing…</span>`);

    try {
      const resp   = await fetch("/api/subscribe", {
        method:  "POST",
        headers: { "Content-Type": "application/json" },
        body:    JSON.stringify({ name, chat_id: chatId, city, topics, channel: "telegram" })
      });
      const result = await resp.json();

      if (result.success) {
        showToast(`✈️ Subscribed! Your daily Telegram brief arrives at <strong>7:00 AM</strong> every morning.`);
        fetchSubscribersCount();
      } else {
        showToast(result.error || "Failed to subscribe.", "error");
      }
    } catch {
      showToast("Network error — could not reach the server.", "error");
    } finally {
      setButtonLoading(btnSubscribe, false, `<span class="btn-icon">✈️</span><span>Subscribe — Get Daily Brief at 7:00 AM</span>`);
    }
  });

  // ── Test sample button ────────────────────────────────────────────────
  btnTestSample.addEventListener("click", async () => {
    const name   = nameInput.value.trim();
    const chatId = chatIdInput?.value.trim() || "";
    const city   = cityInput.value.trim();
    const topics = getSelectedTopics();

    if (!chatId) {
      showToast("Please enter your Telegram Chat ID first.", "error");
      chatIdInput?.focus();
      return;
    }

    setButtonLoading(btnTestSample, true, `<span class="spinner"></span><span>Generating & sending to Telegram…</span>`);

    try {
      const resp   = await fetch("/api/test-dispatch", {
        method:  "POST",
        headers: { "Content-Type": "application/json" },
        body:    JSON.stringify({ name, chat_id: chatId, city, topics })
      });
      const result = await resp.json();

      if (result.success) {
        showToast(`🚀 Sample briefing is being generated and sent to your Telegram right now!`, "success", 6000);
      } else {
        showToast(result.error || "Could not dispatch test.", "error");
      }
    } catch {
      showToast("Network error while sending test.", "error");
    } finally {
      // Small delay so users see the spinner briefly
      setTimeout(() => {
        setButtonLoading(btnTestSample, false, `<span class="btn-icon">🚀</span><span>Send Me a Sample Now</span>`);
      }, 2500);
    }
  });

  // ── Helper: toggle button loading state ───────────────────────────────
  function setButtonLoading(btn, loading, html) {
    btn.disabled   = loading;
    btn.innerHTML  = html;
  }

  // ── Fetch live subscriber count ───────────────────────────────────────
  async function fetchSubscribersCount() {
    try {
      const res  = await fetch("/api/subscribers");
      const data = await res.json();
      if (data?.count !== undefined && subscriberCountEl) {
        // Animate the counter change
        requestAnimationFrame(() => {
          subscriberCountEl.textContent = data.count;
          subscriberCountEl.style.transform = "scale(1.18)";
          setTimeout(() => {
            requestAnimationFrame(() => {
              subscriberCountEl.style.transition = "transform 0.3s ease";
              subscriberCountEl.style.transform  = "scale(1)";
            });
          }, 120);
        });
      }
    } catch { /* quiet fail */ }
  }
});
