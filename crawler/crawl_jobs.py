"""
IT Job crawler for ybox.vn.
Fetches job postings from the ybox.vn CDN API using Playwright.
"""

import asyncio
import json
import time
from pathlib import Path

from playwright.async_api import async_playwright

from parse_job import extract_edges_from_json, posts_to_dataframe

API_BASE = "https://cdn-api.ybox.vn/v1/post"
COMMUNITY_ID = "5a4542f355ae5009afa5a3ec"
PAGES = range(1, 243)          # pages 1–242
CONCURRENT_REQUESTS = 3        # throttle parallel fetches
DELAY_SEC = 0.5                # between batches
MAX_RETRIES = 3
CHECKPOINT_EVERY = 10          # save CSV every N pages

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "data"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
RAW_CSV = OUTPUT_DIR / "raw_jobs.csv"
CHECKPOINT = OUTPUT_DIR / "crawl_state.json"


async def fetch_page(context, page_num: int):
    """Fetch a single page of job data from the CDN API."""
    url = (
        f"{API_BASE}/communityId_{COMMUNITY_ID}"
        f"-newest_25-highlight_15-selective_10-page_{page_num}.json"
    )
    for attempt in range(MAX_RETRIES):
        try:
            resp = await context.request.get(url)
            if resp.ok:
                data = await resp.json()
                edges = extract_edges_from_json(data.get("data", {}).get("AllPosts", {}))
                return edges
            else:
                print(f"  [!] page {page_num} HTTP {resp.status}")
        except Exception as exc:
            print(f"  [!] page {page_num} error: {exc}")
        await asyncio.sleep(2 ** attempt)
    return []


async def crawl():
    """Main crawl orchestration."""
    start = time.time()
    completed_pages = set()
    all_edges = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()

        # Load checkpoint from previous run
        if CHECKPOINT.exists():
            state = json.loads(CHECKPOINT.read_text(encoding="utf-8"))
            completed_pages = set(state.get("pages", []))
            all_edges = state.get("edges", [])
            print(f"[CHK] Resuming — {len(completed_pages)} pages done, "
                  f"{len(all_edges)} edges saved\n")

        # ── Page 1: SSR data from listing page ──────────────────
        if 1 not in completed_pages:
            print("[1/242] Loading listing page (SSR page 1)...")
            listing_page = await context.new_page()
            try:
                await listing_page.goto(
                    "https://ybox.vn/tuyen-dung",
                    wait_until="domcontentloaded",
                    timeout=30000,
                )
                ads = await listing_page.evaluate("window.__INITIAL_ADS__")
                if ads:
                    for source in ("Ads", "Banners", "PremiumBanners"):
                        for edge in ads.get(source, {}).get("edges", []):
                            post = edge.get("post") or edge
                            if post.get("_id") and post.get("title"):
                                all_edges.append(post)
                else:
                    print("  [!] __INITIAL_ADS__ not found")
            except Exception as exc:
                print(f"  [!] page 1 error: {exc}")
            finally:
                await listing_page.close()

            completed_pages.add(1)
            print(f"  -> {len(all_edges)} edges so far\n")

        # ── Pages 2–242: CDN API ───────────────────────────────
        sem = asyncio.Semaphore(CONCURRENT_REQUESTS)

        async def fetch_one(page_num):
            async with sem:
                if page_num in completed_pages:
                    return
                edges = await fetch_page(context, page_num)
                if edges:
                    print(f"  [{page_num}/242] +{len(edges)} jobs")
                    all_edges.extend(edges)
                else:
                    print(f"  [{page_num}/242] (empty)")
                completed_pages.add(page_num)

        # Process in batches with checkpoint saves
        for batch_start in range(2, max(PAGES) + 1, CHECKPOINT_EVERY):
            batch_end = min(batch_start + CHECKPOINT_EVERY, max(PAGES) + 1)
            todo = [n for n in range(batch_start, batch_end) if n not in completed_pages]

            await asyncio.gather(*(fetch_one(n) for n in todo))

            # Save checkpoint
            state = {"pages": list(completed_pages), "edges": all_edges}
            CHECKPOINT.write_text(json.dumps(state), encoding="utf-8")
            await asyncio.sleep(DELAY_SEC)

        await browser.close()

    # ── Final output ───────────────────────────────────────────
    print(f"\nTotal raw edges: {len(all_edges)}")

    df = posts_to_dataframe(all_edges)
    df.to_csv(RAW_CSV, index=False, encoding="utf-8-sig")
    print(f"Saved {len(df)} rows to {RAW_CSV}")

    # Remove checkpoint after success
    CHECKPOINT.unlink(missing_ok=True)

    elapsed = time.time() - start
    print(f"Done in {elapsed:.0f}s ({elapsed/60:.1f} min)")
    return df


def main():
    asyncio.run(crawl())


if __name__ == "__main__":
    main()
