# Vanaras Browser

A web browser for Vanaras agents, served over MCP. Any MCP client or agent (Claude, Gemini, a Vanaras
cloud or desktop vanara) can use it to open pages, read them, click and type. Three rules hold
whatever the model asks:

1. **Personal data never reaches the model.** Pages are redacted before the model sees them. The
   user's saved address becomes `{{HOME_1}}`; emails, phone and card numbers found on a page become
   `{{SEEN_EMAIL_1}}` and the like. The model types `{{HOME_1}}`, and the browser fills in the real
   address locally.
2. **Each vanara stays on its own sites.** Nomm may be limited to food sites and Zipp to travel
   sites. Page loads anywhere else (typed URLs, links, redirects, pop-ups) are stopped before any
   request leaves the machine.
3. **Anything that commits the user waits for a human "yes".** This covers clicking Pay, Place
   order, Send, Delete, Book, Confirm or a form's submit button, and typing into card, password or
   OTP fields. The model has no tool to approve. If nobody can be asked, the answer is no.

It also hides what people can't see. Text hidden with `display:none`, opacity, tiny fonts, clipping,
`aria-hidden` or off-screen positioning is dropped, which is where prompt-injection attacks usually
live. What remains is labelled as website data, not instructions.

## Tools

| Tool | What it does | Risk |
|---|---|---|
| `browser_open` | Open a URL (only allowed sites) and read it | read |
| `browser_read` | Read the current page: visible text and elements with refs (`e1`, `e2`…) | read |
| `browser_click` | Click an element by ref | act, or commit for pay/send/delete/book… |
| `browser_type` | Type into a field; `{{REF}}` references are filled in locally | act, or commit for card/password/OTP |
| `browser_select` | Choose a dropdown option | act |
| `browser_back` | Go back | read |
| `vault_list` | List personal data as references and kinds, never values | read |

There is deliberately no screenshot tool: a screenshot can't be redacted.

## Run it

```bash
npm install && npm run build
node dist/cli.js --name Nomm --allow swiggy.com --allow zomato.com \
  --vault ~/.vanaras/vault.json --profile ~/.vanaras/nomm --log ~/.vanaras/nomm.log.jsonl
```

- `--allow` can be repeated. `example.com` also allows its subdomains, and `"*"` allows any site.
- `--read-only` lets the vanara read pages but not click or type.
- `--profile` keeps the vanara's own cookies and logins between runs.
- `--log` writes an append-only JSON-lines record of every action and approval, using references
  only.
- `--headed` shows the browser window.
- You can put all of this in `--config nomm.json`: `{ "vanara": { "name", "allowedDomains", "canAct", "commitWords" }, "vault", "profileDir", "log" }`.

The vault is a local file the model never sees:

```json
[
  { "ref": "HOME_1", "kind": "address", "value": "12 MG Road, Bengaluru 560001" },
  { "ref": "PHONE_1", "kind": "phone", "value": "+91 98765 43210" }
]
```

Chromium comes from `VANARAS_CHROMIUM`, or Playwright's installed browser.

### In Claude Code or any MCP client

```json
{ "mcpServers": { "nomm-browser": { "command": "node",
  "args": ["/path/to/vanaras-browser/dist/cli.js", "--name", "Nomm", "--allow", "swiggy.com", "--vault", "/path/vault.json"] } } }
```

Approvals use MCP elicitation, so the client asks the user. A client without elicitation gets a
"no" for every commit. Embedders can pass their own `approver` to `createServer`, for example one
that sends the approval to the user's phone.

## Tests

`npm test` runs 20 tests. The browser tests drive a real Chromium through the MCP protocol against a
local test shop. They check:

- that no personal data or hidden instruction reaches the model;
- that paying waits for approval, and a "no" leaves the page unpaid;
- that references are typed as real values;
- that card fields need approval;
- that links to other sites are blocked;
- that the log holds no personal data.

## Limits (v0.1)

- Only the saved vault plus email, phone and card patterns are redacted. Names and free-text
  personal details on a page are not detected yet.
- Commit detection works from button labels, field types and the site. A site that labels its
  buy button with an icon alone reads as an ordinary click. Add words per vanara with
  `commitWords`.
- One tab per vanara, and no file downloads or uploads.
