"""
check_graphiti.py - Diagnostik Ringan Graphiti Memory
========================================================
Script ini BUKAN untuk testing penuh, hanya untuk MELIHAT:
1. Apakah Neo4j bisa diakses?
2. Apakah Graphiti singleton bisa dibuat?
3. Apakah ada data (node/edge) yang sudah tersimpan di Neo4j?
4. Apa saja episode yang sudah ada untuk setiap patient?

Jalankan: python check_graphiti.py
Output: plain text, tidak ada emoji, tidak berat.
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


async def check_neo4j_raw():
    """Cek koneksi Neo4j secara langsung via neo4j driver, tanpa Graphiti."""
    print("\n[1/4] Mengecek koneksi Neo4j secara langsung...")
    try:
        from neo4j import AsyncGraphDatabase
        uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        user = os.getenv("NEO4J_USER", "neo4j")
        password = os.getenv("NEO4J_PASSWORD", "password")

        async with AsyncGraphDatabase.driver(uri, auth=(user, password)) as driver:
            async with driver.session() as session:
                result = await session.run("RETURN 1 AS ping")
                rec = await result.single()
                print(f"  Neo4j OK - ping={rec['ping']}")

                # Hitung total node
                r2 = await session.run("MATCH (n) RETURN count(n) AS total_nodes")
                row = await r2.single()
                print(f"  Total Nodes di Neo4j: {row['total_nodes']}")

                # Hitung total relationship
                r3 = await session.run("MATCH ()-[r]->() RETURN count(r) AS total_rel")
                row3 = await r3.single()
                print(f"  Total Relationships : {row3['total_rel']}")

                # Lihat label-label node yang ada
                r4 = await session.run("CALL db.labels() YIELD label RETURN label")
                labels = [rec["label"] async for rec in r4]
                print(f"  Node Labels ada     : {labels if labels else '(kosong - belum ada data)'}")

                # Lihat group_id yang ada (ini = data tiap pasien)
                r5 = await session.run(
                    "MATCH (n) WHERE n.group_id IS NOT NULL "
                    "RETURN DISTINCT n.group_id AS gid LIMIT 20"
                )
                groups = [rec["gid"] async for rec in r5]
                if groups:
                    print(f"  Patient Groups ada  : {groups}")
                else:
                    print(f"  Patient Groups ada  : (belum ada - memory belum pernah menyimpan apapun)")

        return True
    except Exception as e:
        print(f"  [ERROR] Neo4j tidak bisa diakses: {type(e).__name__}: {e}")
        return False


async def check_graphiti_init():
    """Coba inisialisasi Graphiti (tanpa add/search data)."""
    print("\n[2/4] Menginisialisasi Graphiti singleton...")
    try:
        from memory.graphiti_client import get_graphiti, close_graphiti
        g = await get_graphiti()
        print(f"  Graphiti OK - instance: {type(g).__name__}")
        await close_graphiti()
        return True
    except Exception as e:
        print(f"  [ERROR] Graphiti gagal init: {type(e).__name__}: {e}")
        return False


async def check_episodes_in_neo4j():
    """Ambil episode/fact yang sudah tersimpan dari Neo4j langsung."""
    print("\n[3/4] Mencari episode yang sudah tersimpan di Neo4j...")
    try:
        from neo4j import AsyncGraphDatabase
        uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        user = os.getenv("NEO4J_USER", "neo4j")
        password = os.getenv("NEO4J_PASSWORD", "password")

        async with AsyncGraphDatabase.driver(uri, auth=(user, password)) as driver:
            async with driver.session() as session:
                # Graphiti menyimpan episode di node dengan label EpisodicNode
                r = await session.run(
                    "MATCH (e:EpisodicNode) "
                    "RETURN e.group_id AS gid, e.name AS name, e.content AS content "
                    "ORDER BY e.created_at DESC LIMIT 10"
                )
                episodes = []
                async for rec in r:
                    episodes.append({
                        "group": rec["gid"],
                        "name": rec["name"],
                        "content": (rec["content"] or "")[:100] + "..." if rec["content"] and len(rec["content"]) > 100 else rec["content"]
                    })

                if episodes:
                    print(f"  Ditemukan {len(episodes)} episode (max 10 terbaru):")
                    for ep in episodes:
                        print(f"    Patient={ep['group']} | {ep['name']}")
                        print(f"      -> {ep['content']}")
                else:
                    print("  Tidak ada EpisodicNode - memory belum pernah menyimpan episode apapun.")

                # Cek EntityNode (entity yang diekstrak Graphiti)
                r2 = await session.run(
                    "MATCH (e:EntityNode) "
                    "RETURN e.name AS name, e.group_id AS gid "
                    "LIMIT 10"
                )
                entities = [f"{rec['name']} ({rec['gid']})" async for rec in r2]
                if entities:
                    print(f"\n  Entity yang diekstrak Graphiti (max 10): {entities}")
                else:
                    print(f"\n  Tidak ada EntityNode - Graphiti belum mengekstrak entitas apapun.")

                # Cek EdgeNode (relasi/fact)
                r3 = await session.run(
                    "MATCH (e:EntityEdge) "
                    "RETURN e.fact AS fact, e.group_id AS gid "
                    "LIMIT 10"
                )
                edges = []
                async for rec in r3:
                    edges.append(f"  Fact: {rec['fact']} | Group: {rec['gid']}")
                if edges:
                    print(f"\n  Facts/Relationships yang tersimpan (max 10):")
                    for edge in edges:
                        print(f"    {edge}")
                else:
                    print(f"\n  Tidak ada EntityEdge/Fact - Graphiti belum mengekstrak relasi apapun.")

    except Exception as e:
        print(f"  [ERROR]: {type(e).__name__}: {e}")


async def check_graphiti_search():
    """Coba query Graphiti search - apakah bisa retrieve data?"""
    print("\n[4/4] Test Graphiti search query...")
    try:
        from memory.graphiti_client import get_graphiti, close_graphiti
        g = await get_graphiti()

        # Search tanpa group_id dulu - cari semua
        results = await g.search(
            query="patient heart rate monitoring",
            num_results=5
        )

        if results:
            print(f"  Search berhasil! Ditemukan {len(results)} fakta:")
            for i, edge in enumerate(results, 1):
                fact = str(getattr(edge, 'fact', str(edge)))
                print(f"    {i}. {fact[:120]}")
        else:
            print("  Search kosong - belum ada data di memori Graphiti.")

        await close_graphiti()

    except Exception as e:
        print(f"  [ERROR] Graphiti search gagal: {type(e).__name__}: {e}")


async def main():
    print("=" * 60)
    print("DIAGNOSTIK GRAPHITI MEMORY - UTLMediCore")
    print("=" * 60)

    neo4j_ok = await check_neo4j_raw()

    if not neo4j_ok:
        print("\nNeo4j tidak bisa diakses. Pastikan Neo4j Desktop sedang berjalan.")
        print("Default: bolt://localhost:7687 | user: neo4j | pass: password")
        return

    await check_episodes_in_neo4j()
    await check_graphiti_init()
    await check_graphiti_search()

    print("\n" + "=" * 60)
    print("DIAGNOSTIK SELESAI")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
