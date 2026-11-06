import assert from "node:assert/strict";
import { test } from "node:test";
import { Vault } from "../src/vault.ts";

const vault = () => new Vault([
  { ref: "HOME_1", kind: "address", value: "12 MG Road, Bengaluru 560001" },
  { ref: "CARD_1", kind: "card", value: "4111 1111 1111 1111" },
]);

test("saved values become references", () => {
  const v = vault();
  assert.equal(v.redact("Deliver to 12 MG  Road, bengaluru 560001 today"), "Deliver to {{HOME_1}} today");
  assert.equal(v.redact("Card 4111 1111 1111 1111"), "Card {{CARD_1}}");
});

test("personal data seen on pages gets stable references", () => {
  const v = vault();
  const out = v.redact("Mail priya@example.com, call +91 98765 43210, mail priya@example.com again");
  assert.equal(out, "Mail {{SEEN_EMAIL_1}}, call {{SEEN_PHONE_1}}, mail {{SEEN_EMAIL_1}} again");
  assert.equal(v.resolve("{{SEEN_EMAIL_1}}"), "priya@example.com");
});

test("order numbers and prices are not mistaken for cards or phones", () => {
  const v = vault();
  assert.equal(v.redact("Order #1234567890123 total ₹450, pin 560001"), "Order #1234567890123 total ₹450, pin 560001");
  assert.equal(v.redact("card 5500 0000 0000 0004"), "card {{SEEN_CARD_1}}"); // passes Luhn
});

test("references resolve locally; unknown ones are refused", () => {
  const v = vault();
  assert.equal(v.resolve("Ship to {{HOME_1}}"), "Ship to 12 MG Road, Bengaluru 560001");
  assert.throws(() => v.resolve("{{HOME_9}}"), /Unknown reference/);
});

test("the model can list references but never values", () => {
  const listed = JSON.stringify(vault().list());
  assert.match(listed, /HOME_1/);
  assert.doesNotMatch(listed, /MG Road|4111/);
});

test("bad references are rejected when loading", () => {
  assert.throws(() => new Vault([{ ref: "home-1", kind: "address", value: "x" }]), /Bad vault reference/);
});
