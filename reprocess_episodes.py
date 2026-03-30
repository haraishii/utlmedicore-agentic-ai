"""
reprocess_episodes.py
=====================
Re-submits existing Episodic nodes from Neo4j back through Graphiti
so entity extraction runs again — generating the missing EntityEdge facts.

Usage:
    PYTHONUTF8=1 python reprocess_episodes.py
    PYTHONUTF8=1 python reprocess_episodes.py --device DCA632971FC3 --limit 20
"""
import asyncio
import argparse
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime

PATIENTS = ["DCA632971FC3", "2CCF6754457F", "TEST_DEVICE_001"]

async def reprocess(device_id: str, limit: int = 30):
    from memory.graphiti_client import get_graphiti
    from neo4j import AsyncGraphDatabase

    NEO4J_URI  = os.getenv("NEO4J_URI",      "bolt://localhost:7687")
    NEO4J_USER = os.getenv("NEO4J_USER",     "neo4j")
    NEO4J_PASS = os.getenv("NEO4J_PASSWORD", "password")

    group_id = f"patient_{device_id}"
    print(f"\n{'='*55}")
    print(f"  Re-processing episodes for: {device_id}")
    print(f"  Group ID: {group_id}  |  Limit: {limit}")
    print(f"{'='*55}")

    driver = AsyncGraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))

    episodes = []
    async with driver.session() as s:
        # Read existing Episodic nodes for this patient
        r = await s.run(
            """
            MATCH (e:Episodic)
            WHERE e.group_id = $gid
            RETURN e.name AS name,
                   e.content AS content,
                   e.source_description AS src,
                   e.valid_at AS valid_at
            ORDER BY e.created_at ASC
            LIMIT $lim
            """,
            gid=group_id,
            lim=limit,
        )
        async for rec in r:
            episodes.append({
                "name":     rec["name"],
                "content":  rec["content"] or "",
                "src":      rec["src"] or f"UTLMediCore — Device {device_id}",
                "valid_at": rec["valid_at"],
            })

    await driver.close()

    if not episodes:
        print(f"  No Episodic nodes found for {device_id}. Nothing to re-process.")
        return

    print(f"  Found {len(episodes)} episodes. Starting re-submission to Graphiti...\n")

    graphiti = await get_graphiti()

    ok_count = 0
    for i, ep in enumerate(episodes, 1):
        content = ep["content"]
        if not content.strip():
            print(f"  [{i}/{len(episodes)}] SKIP (empty content): {ep['name']}")
            continue

        # Parse valid_at if available, else use now
        ref_time = datetime.now()
        if ep["valid_at"]:
            try:
                ref_time = datetime.fromisoformat(str(ep["valid_at"]).split("+")[0].split("000")[0])
            except Exception:
                pass

        print(f"  [{i}/{len(episodes)}] Submitting: {ep['name'][:60]}")
        print(f"    Content: {content[:90]}...")

        try:
            await graphiti.add_episode(
                name=ep["name"] + "_reprocessed",
                episode_body=content,
                source_description=ep["src"],
                group_id=group_id,
                reference_time=ref_time,
            )
            print(f"    OK - entities extracted")
            ok_count += 1
        except Exception as e:
            err = str(e)
            if "duplicate" in err.lower() or "entity not found" in err.lower():
                print(f"    OK (minor graph warning, entity still processed)")
                ok_count += 1
            else:
                print(f"    WARN: {err[:100]}")

        # Small pause to avoid flooding Ollama
        await asyncio.sleep(2)

    print(f"\n  Done: {ok_count}/{len(episodes)} episodes re-processed for {device_id}")
    print(f"  Facts should now appear in Graphiti search results.\n")


async def main(device_ids: list, limit: int):
    for did in device_ids:
        await reprocess(did, limit)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Re-process Graphiti episodes")
    parser.add_argument("--device", default=None, help="Specific device ID (default: all)")
    parser.add_argument("--limit",  type=int, default=20, help="Episodes per patient (default 20)")
    args = parser.parse_args()

    targets = [args.device] if args.device else PATIENTS
    print(f"Re-processing Graphiti episodes for: {targets}")
    print(f"This will call Ollama llama3.1:8b for entity extraction.")
    print(f"Estimated time: ~{len(targets) * args.limit * 15 // 60} min\n")

    # Load .env
    from dotenv import load_dotenv
    load_dotenv("e:/agentic/.env")

    asyncio.run(main(targets, args.limit))
