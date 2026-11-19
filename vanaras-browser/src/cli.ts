#!/usr/bin/env node
/**
 * Runs the Vanaras browser over stdio.
 *
 *   vanaras-browser --config nomm.json
 *   vanaras-browser --name Nomm --allow swiggy.com --allow zomato.com --vault ~/.vanaras/vault.json
 *
 * The vault file holds personal data as [{ "ref": "HOME_1", "kind": "address", "value": "…" }].
 * Keep it out of the config you share; only references ever reach the model.
 */
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { readFileSync } from "node:fs";
import { parseArgs } from "node:util";
import type { VanaraPolicy } from "./policy.js";
import { createServer } from "./server.js";
import { Vault, type VaultEntry } from "./vault.js";

interface Config {
  vanara?: Partial<VanaraPolicy>;
  vault?: string;
  profileDir?: string;
  log?: string;
  headless?: boolean;
}

const { values } = parseArgs({
  options: {
    config: { type: "string" },
    name: { type: "string" },
    allow: { type: "string", multiple: true },
    "read-only": { type: "boolean" },
    vault: { type: "string" },
    profile: { type: "string" },
    log: { type: "string" },
    headed: { type: "boolean" },
  },
});

const config: Config = values.config ? JSON.parse(readFileSync(values.config, "utf8")) : {};
const policy: VanaraPolicy = {
  name: values.name ?? config.vanara?.name ?? "Vanara",
  allowedDomains: values.allow ?? config.vanara?.allowedDomains ?? [],
  canAct: values["read-only"] ? false : config.vanara?.canAct ?? true,
  commitWords: config.vanara?.commitWords,
};
if (policy.allowedDomains.length === 0) {
  console.error("vanaras-browser: no sites allowed. Pass --allow example.com (or \"*\" for any site).");
  process.exit(2);
}
const vaultPath = values.vault ?? config.vault;
const entries: VaultEntry[] = vaultPath ? JSON.parse(readFileSync(vaultPath, "utf8")) : [];

const { server, close } = createServer({
  policy,
  vault: new Vault(entries),
  browser: { profileDir: values.profile ?? config.profileDir, headless: values.headed ? false : config.headless ?? true },
  logFile: values.log ?? config.log,
});
await server.connect(new StdioServerTransport());
const stop = async () => {
  await close().catch(() => {});
  process.exit(0);
};
process.on("SIGINT", stop);
process.on("SIGTERM", stop);
