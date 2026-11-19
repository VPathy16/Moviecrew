import assert from "node:assert/strict";
import { test } from "node:test";
import { clickRisk, hostAllowed, typeRisk, type VanaraPolicy } from "../src/policy.ts";

const nomm: VanaraPolicy = { name: "Nomm", allowedDomains: ["swiggy.com", "zomato.com"], canAct: true };

test("a vanara only opens its own sites", () => {
  assert.ok(hostAllowed(nomm, "https://www.swiggy.com/restaurants"));
  assert.ok(hostAllowed(nomm, "https://zomato.com"));
  assert.ok(!hostAllowed(nomm, "https://swiggy.com.evil.test/"));
  assert.ok(!hostAllowed(nomm, "https://notswiggy.com/"));
  assert.ok(!hostAllowed(nomm, "file:///etc/passwd"));
  assert.ok(!hostAllowed(nomm, "javascript:alert(1)"));
  assert.ok(hostAllowed({ ...nomm, allowedDomains: ["*"] }, "https://anything.test"));
});

test("clicks that commit the user are commits", () => {
  for (const name of ["Pay now", "Place order", "PLACE ORDER ₹450", "Send", "Delete account", "Book table", "Confirm"])
    assert.equal(clickRisk(nomm, { role: "button", name }), "commit", name);
  for (const name of ["Add to cart", "Menu", "Paypal info", "Sender details", "Bookmarks"])
    assert.equal(clickRisk(nomm, { role: "button", name }), "act", name);
  assert.equal(clickRisk(nomm, { role: "button", name: "Next", type: "submit" }), "commit");
  assert.equal(clickRisk({ ...nomm, commitWords: ["tip"] }, { role: "button", name: "Add tip" }), "commit");
});

test("typing into card, password or OTP fields is a commit", () => {
  assert.equal(typeRisk({ name: "Card number", autocomplete: "cc-number" }), "commit");
  assert.equal(typeRisk({ name: "Password", type: "password" }), "commit");
  assert.equal(typeRisk({ name: "Enter OTP" }), "commit");
  assert.equal(typeRisk({ name: "Search restaurants" }), "act");
});
