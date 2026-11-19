/**
 * Personal data the model must never see.
 *
 * The vault holds the user's saved values (addresses, phone, card…) under references like HOME_1.
 * Everything the browser sends to the model goes through `redact`, which swaps those values, and
 * anything that looks personal (emails, phone and card numbers), for references. Everything the
 * model sends back goes through `resolve`, which swaps `{{REF}}` for the real value, locally.
 */

export interface VaultEntry {
  /** What the model sees and writes, e.g. HOME_1. Letters, digits and underscores. */
  ref: string;
  /** What it is, e.g. "address", "phone", "email", "card", "name". Shown to the model. */
  kind: string;
  /** The real value. Never leaves this process. */
  value: string;
}

/** Personal data found on pages without being saved in the vault. */
const PATTERNS: { kind: string; regex: RegExp; valid?: (s: string) => boolean }[] = [
  { kind: "EMAIL", regex: /[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}/g },
  // 13–19 digits in groups: payment cards. Luhn keeps order numbers and the like out.
  { kind: "CARD", regex: /\b(?:\d[ -]?){12,18}\d\b/g, valid: (s) => luhn(s.replace(/\D/g, "")) },
  // Phone numbers: "+91 98765 43210", "(020) 7946 0958", "9876543210". A bare run of digits only
  // counts when it is exactly 10 long, so order and tracking numbers stay readable.
  { kind: "PHONE", regex: /(?<![\w#])(?:\+\d{1,3}[ .-]?)?(?:\(\d{2,5}\)[ .-]?)?\d{2,5}(?:[ .-]?\d{2,5}){1,3}(?!\w)/g,
    valid: (s) => {
      const digits = s.replace(/\D/g, "").length;
      if (digits < 10 || digits > 13) return false;
      return s.trim().startsWith("+") || s.trim().startsWith("(") || /[ .-]/.test(s.trim()) || digits === 10;
    } },
];

const REF_TOKEN = /\{\{([A-Z][A-Z0-9_]*)\}\}/g;

export class Vault {
  private readonly byRef = new Map<string, VaultEntry>();
  /** References minted for personal data seen on pages, so the model can still use it. */
  private readonly seen = new Map<string, string>(); // value -> ref
  private counters = new Map<string, number>();

  constructor(entries: VaultEntry[] = []) {
    for (const e of entries) {
      if (!/^[A-Z][A-Z0-9_]*$/.test(e.ref)) throw new Error(`Bad vault reference "${e.ref}": use A–Z, 0–9 and _`);
      if (!e.value) continue;
      this.byRef.set(e.ref, e);
    }
  }

  /** What the model may know: references and kinds, never values. */
  list(): { ref: string; kind: string }[] {
    return [...this.byRef.values()].map(({ ref, kind }) => ({ ref, kind }));
  }

  /** Replaces personal data in text bound for the model with {{REF}} tokens. */
  redact(text: string): string {
    if (!text) return text;
    let out = text;
    // Longest values first, so "12 MG Road, Bengaluru" wins over "Bengaluru".
    const saved = [...this.byRef.values()].sort((a, b) => b.value.length - a.value.length);
    for (const e of saved) out = replaceAllLoose(out, e.value, `{{${e.ref}}}`);
    for (const p of PATTERNS) {
      out = out.replace(p.regex, (match) => {
        if (match.includes("{{")) return match;
        if (p.valid && !p.valid(match)) return match;
        return `{{${this.mint(p.kind, match.trim())}}}`;
      });
    }
    return out;
  }

  /** Swaps {{REF}} tokens for real values. Unknown references are an error, never passed through. */
  resolve(text: string): string {
    return text.replace(REF_TOKEN, (_m, ref: string) => {
      const saved = this.byRef.get(ref);
      if (saved) return saved.value;
      for (const [value, r] of this.seen) if (r === ref) return value;
      throw new Error(`Unknown reference {{${ref}}}. Call vault_list to see the ones you can use.`);
    });
  }

  /** Whether text still contains a value the vault protects (a leak check for tests and logs). */
  containsSecret(text: string): boolean {
    for (const e of this.byRef.values()) if (normalize(text).includes(normalize(e.value))) return true;
    return false;
  }

  private mint(kind: string, value: string): string {
    const known = this.seen.get(value);
    if (known) return known;
    const n = (this.counters.get(kind) ?? 0) + 1;
    this.counters.set(kind, n);
    const ref = `SEEN_${kind}_${n}`;
    this.seen.set(value, ref);
    return ref;
  }
}

function normalize(s: string): string {
  return s.replace(/\s+/g, " ").trim().toLowerCase();
}

/** Replaces `needle` in `hay` ignoring case and differences in whitespace. */
function replaceAllLoose(hay: string, needle: string, replacement: string): string {
  const words = needle.trim().split(/\s+/).map(escapeRegex);
  if (words.length === 0 || words[0] === "") return hay;
  return hay.replace(new RegExp(words.join("\\s+"), "gi"), replacement);
}

function escapeRegex(s: string): string {
  return s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

function luhn(digits: string): boolean {
  if (digits.length < 13 || digits.length > 19) return false;
  let sum = 0;
  for (let i = 0; i < digits.length; i++) {
    let d = Number(digits[digits.length - 1 - i]);
    if (i % 2 === 1) {
      d *= 2;
      if (d > 9) d -= 9;
    }
    sum += d;
  }
  return sum % 10 === 0;
}
