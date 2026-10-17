# Quiz Qrusher: to-do

Ideas and planned work after v3.0. Read [V3_PLAN.md](V3_PLAN.md) before building any of these.

## AI generation in the app (v3.1 candidate)

Added 2026-10-16. Third-party sites can't use a Claude Pro, ChatGPT Plus or Gemini Advanced subscription; those plans only work in each provider's own apps. Users with only a subscription keep the copy-and-paste pipeline, so it stays.

- [ ] **"Copy & open" buttons** in the Prompt Builder: each step copies its prompt and opens a new chat in the recommended model (Claude, ChatGPT or Gemini). Users still attach files by hand. No cost or key needed.
- [ ] **Optional "Generate here" with the user's own API key** (Anthropic, OpenAI or Google):
  - Keep the key only in the browser, and the requests go straight from the page to the provider. Anthropic needs the `anthropic-dangerous-direct-browser-access: true` header for browser calls.
  - Run the whole pipeline (slide miner → style researcher → question generator) in one go and load the CSV automatically.
  - Turn the style researcher's questions into a short form.
  - Point users who don't want to pay to a free-tier Gemini API key.
- [ ] **Alternative: "Connect OpenRouter."** Users approve access on OpenRouter's site and come back connected (OAuth PKCE works from a static page). One connection reaches Claude, GPT and Gemini models, paid from prepaid credits.
- Constraints:
  - Full app only. Lite stays offline.
  - No SDK from a CDN; use `fetch`.
  - Never write the key into saves, bundles or the saves folder.
  - Reword "Nothing is uploaded" in the README and Help → Privacy to say that slides go to the chosen provider.
