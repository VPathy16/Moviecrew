/**
 * What one vanara may do in the browser, and how risky each action is.
 *
 * A vanara is scoped: Nomm may browse food sites, Zipp travel sites, and neither can wander off.
 * Every action gets a risk level; anything that commits the user (pay, send, delete, book…)
 * needs a human "yes" before it runs, whatever the model says.
 */

export type Risk = "read" | "act" | "commit";

export interface VanaraPolicy {
  /** The vanara's name, used in approvals and the log. */
  name: string;
  /** Sites it may open. "example.com" also allows its subdomains; "*" allows any site. */
  allowedDomains: string[];
  /** Whether it may click and type at all, or only read. */
  canAct: boolean;
  /** Extra words that make a click a commit for this vanara (on top of the defaults). */
  commitWords?: string[];
}

export const READ_ONLY: VanaraPolicy = { name: "Reader", allowedDomains: ["*"], canAct: false };

/** Button and link labels that commit the user to something. Matched as words, any case. */
const COMMIT_WORDS = [
  "pay", "pay now", "buy", "buy now", "purchase", "place order", "order now", "checkout", "check out",
  "confirm", "submit", "send", "post", "publish", "delete", "remove", "cancel", "unsubscribe",
  "transfer", "withdraw", "book", "reserve", "subscribe", "sign up", "register", "apply",
  "authorize", "authorise", "approve", "donate",
];

/** Field types whose contents are sensitive: typing into them needs approval. */
const SENSITIVE_FIELDS = /password|card|cc-|cvv|cvc|otp|one-time|pin|iban|account|ssn|aadhaar|pan\b/i;

export function hostAllowed(policy: VanaraPolicy, url: string): boolean {
  let host: string;
  try {
    const u = new URL(url);
    if (u.protocol === "about:") return true;
    if (u.protocol !== "http:" && u.protocol !== "https:") return false;
    host = u.hostname.toLowerCase();
  } catch {
    return false;
  }
  return policy.allowedDomains.some((d) => {
    const domain = d.toLowerCase().replace(/^\*\./, "");
    return domain === "*" || host === domain || host.endsWith(`.${domain}`);
  });
}

/** The risk of clicking an element with this role and accessible name. */
export function clickRisk(policy: VanaraPolicy, el: { role: string; name: string; type?: string }): Risk {
  const words = [...COMMIT_WORDS, ...(policy.commitWords ?? [])];
  const label = el.name.toLowerCase();
  if (el.type === "submit") return "commit";
  if (words.some((w) => new RegExp(`(^|[^a-z])${escapeRegex(w)}([^a-z]|$)`).test(label))) return "commit";
  return "act";
}

/** The risk of typing into a field described by its type, name and autocomplete hint. */
export function typeRisk(field: { name: string; type?: string; autocomplete?: string }): Risk {
  const hint = `${field.type ?? ""} ${field.autocomplete ?? ""} ${field.name}`;
  return SENSITIVE_FIELDS.test(hint) ? "commit" : "act";
}

function escapeRegex(s: string): string {
  return s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}
