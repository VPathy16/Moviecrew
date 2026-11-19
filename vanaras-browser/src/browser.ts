/**
 * The browser itself: one Chromium profile per vanara, and a page reader built for agents.
 *
 * The reader returns only what a person can see: hidden text (display:none, opacity 0, tiny or
 * off-screen) is dropped, which is where prompt-injection attacks usually hide. Interactive
 * elements get short references (e1, e2…) that the model uses to click and type.
 */
import { chromium, type BrowserContext, type Page } from "playwright-core";
import { existsSync } from "node:fs";
import { READ_PAGE } from "./reader.js";

export interface PageElement {
  ref: string;
  role: string;
  name: string;
  /** Input type (text, email, password, submit…), when it is a form field or button. */
  type?: string;
  autocomplete?: string;
  value?: string;
  /** Options of a <select>. */
  options?: string[];
  disabled?: boolean;
}

export interface PageView {
  url: string;
  title: string;
  text: string;
  elements: PageElement[];
}

export interface BrowserOptions {
  /** Where the vanara's profile (cookies, logins) lives. Omit for a throwaway profile. */
  profileDir?: string;
  headless?: boolean;
  executablePath?: string;
  /** Longest page text returned, in characters. */
  maxText?: number;
  /** Pages the browser may navigate to; other page loads (links, redirects, pop-ups) are blocked. */
  allowNavigation?: (url: string) => boolean;
}

const DEFAULT_CHROMIUM = [
  process.env.VANARAS_CHROMIUM,
  "/opt/pw-browsers/chromium-1194/chrome-linux/chrome",
].filter((p): p is string => !!p);

export class Browser {
  private context?: BrowserContext;
  private page?: Page;
  private launched?: import("playwright-core").Browser;
  /** The last page load that was blocked, reported with the next action. */
  blocked?: string;

  constructor(private readonly options: BrowserOptions = {}) {}

  async current(): Promise<Page> {
    if (this.page && !this.page.isClosed()) return this.page;
    if (!this.context) {
      const executablePath = this.options.executablePath ?? DEFAULT_CHROMIUM.find((p) => existsSync(p));
      const launch = { headless: this.options.headless ?? true, executablePath };
      if (this.options.profileDir) {
        this.context = await chromium.launchPersistentContext(this.options.profileDir, launch);
      } else {
        this.launched = await chromium.launch(launch);
        this.context = await this.launched.newContext();
      }
      const allow = this.options.allowNavigation;
      if (allow) {
        // Stop page loads to other sites, in any frame; sub-resources (images, scripts) still load.
        await this.context.route("**/*", (route) => {
          const request = route.request();
          if (request.isNavigationRequest() && !allow(request.url())) {
            this.blocked = request.url();
            // A 204 answer to a page load leaves the tab where it was, instead of on an error page.
            return route.fulfill({ status: 204, body: "" });
          }
          return route.continue();
        });
      }
      // A page opened by a click becomes the current page.
      this.context.on("page", (p) => (this.page = p));
    }
    this.page = this.context.pages()[0] ?? (await this.context.newPage());
    return this.page;
  }

  async open(url: string): Promise<void> {
    const page = await this.current();
    await page.goto(url, { waitUntil: "domcontentloaded", timeout: 30_000 });
    await settle(page);
  }

  async back(): Promise<void> {
    const page = await this.current();
    await page.goBack({ waitUntil: "domcontentloaded" });
    await settle(page);
  }

  /** What is on the page now, for the model (before redaction). */
  async read(): Promise<PageView> {
    const page = await this.current();
    // Read a little past the limit; the caller redacts, then trims, so no value is cut in half.
    const maxText = (this.options.maxText ?? 12_000) + 1_000;
    const view = (await page.evaluate(`(${READ_PAGE})(${maxText})`)) as { text: string; elements: PageElement[] };
    return { url: page.url(), title: await page.title(), ...view };
  }

  async click(ref: string): Promise<void> {
    const page = await this.current();
    await page.locator(selector(ref)).click({ timeout: 10_000 });
    await settle(page);
  }

  async type(ref: string, text: string, submit: boolean): Promise<void> {
    const page = await this.current();
    const field = page.locator(selector(ref));
    await field.fill(text, { timeout: 10_000 });
    if (submit) {
      await field.press("Enter");
      await settle(page);
    }
  }

  async select(ref: string, option: string): Promise<void> {
    const page = await this.current();
    await page.locator(selector(ref)).selectOption({ label: option }, { timeout: 10_000 });
  }

  async close(): Promise<void> {
    await this.context?.close();
    await this.launched?.close();
    this.context = undefined;
    this.launched = undefined;
    this.page = undefined;
  }
}

function selector(ref: string): string {
  if (!/^e\d+$/.test(ref)) throw new Error(`"${ref}" is not an element reference; use one from browser_read`);
  return `[data-vanaras-ref="${ref}"]`;
}

async function settle(page: Page): Promise<void> {
  await page.waitForLoadState("domcontentloaded").catch(() => {});
  await page.waitForLoadState("networkidle", { timeout: 3_000 }).catch(() => {});
}
