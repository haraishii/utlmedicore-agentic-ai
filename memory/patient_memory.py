"""
PatientMemory: Graphiti-backed persistent memory for UTLMediCore patients.
===========================================================================

This class wraps the Graphiti knowledge graph to provide:
- add_episode()           : Store any notable event (alert, observation, baseline)
- get_patient_context()   : Query patient history before making an agent decision
- store_alert()           : Persist an alert so future sessions remember it
- store_sensor_snapshot() : Convert raw sensor data to a human-readable memory episode

Design choices:
- Each patient is isolated via group_id = "patient_{device_id}"
- Episodes are stored as natural language for best LLM understanding
- run_async() helper bridges async Graphiti with sync Flask/SocketIO
"""

import asyncio
import concurrent.futures
from datetime import datetime
from typing import Optional

from memory.graphiti_client import get_graphiti


# ---------------------------------------------------------------------------
# POSTURE & AREA TEXT MAPS (duplicated here to avoid circular imports)
# ---------------------------------------------------------------------------
_POSTURE_MAP = {
    0: "Unknown", 1: "Sitting", 2: "Standing", 3: "Lying Down",
    4: "Lying on Right Side", 5: "Falling", 6: "Prone",
    7: "Lying on Left Side", 8: "Walking", 10: "Unstable",
    11: "Upright Torso"
}

_AREA_MAP = {
    1: "Unknown Area", 2: "Laboratory", 3: "Corridor",
    4: "Dining Table", 5: "Living Room", 6: "Bathroom",
    7: "Bedroom", 8: "Laboratory"
}


# ---------------------------------------------------------------------------
# ASYNC BRIDGE (run Graphiti coroutines from synchronous Flask/SocketIO)
# ---------------------------------------------------------------------------
import threading

_async_loop = None
_loop_thread = None
_llm_lock = None  # Prevents Ollama from getting flooded by concurrent requests

def _start_background_loop(loop):
    """Run the event loop in a dedicated background thread."""
    asyncio.set_event_loop(loop)
    loop.run_forever()

async def _locked_coro(coro):
    """Wrapper to force LLM tasks to execute strictly one at a time."""
    global _llm_lock
    if _llm_lock is None:
        _llm_lock = asyncio.Lock()
    async with _llm_lock:
        return await coro

def _future_done_callback(fut):
    try:
        fut.result()
    except Exception as e:
        err_type = type(e).__name__
        err_str = str(e)
        if "Timeout" in err_type or "Timeout" in err_str:
            print("[Memory Background Error] Ollama Request Timed Out (Beban Terlalu Berat).")
        elif "Target entity not found" in err_str or "duplicate" in err_str or "validation" in err_str.lower():
            pass # Silent skip
        else:
            print(f"[Memory Background Error] ({err_type}): {err_str}")

def run_async(coro, wait_result=True):
    """
    Run an async coroutine safely from a synchronous eventlet/gevent context.
    Uses a single, dedicated background thread running an asyncio event loop.
    ALL calls go through the LLM lock to serialize Ollama traffic.
    """
    global _async_loop, _loop_thread
    
    if _async_loop is None:
        _async_loop = asyncio.new_event_loop()
        _loop_thread = threading.Thread(
            target=_start_background_loop, 
            args=(_async_loop,), 
            daemon=True
        )
        _loop_thread.start()
        
    # Wraps the user's coro in our lock to serialize Ollama traffic
    safe_coro = _locked_coro(coro)
    
    # Submit the coroutine to the background loop
    future = asyncio.run_coroutine_threadsafe(safe_coro, _async_loop)
    
    if not wait_result:
        future.add_done_callback(_future_done_callback)
        return None
        
    try:
        # Provide longer timeout (60s) for slow local LLM extraction
        return future.result(timeout=60)
    except Exception as e:
        err_type = type(e).__name__
        err_str = str(e)
        
        if "Timeout" in err_type or "Timeout" in err_str:
            print("[Memory Agent] LLM took too long to respond (Timeout). Skipped.")
        elif "Target entity not found" in err_str or "duplicate" in err_str or "validation" in err_str.lower():
            pass # Silent skip
        else:
            print(f"[Memory Agent] Minor skip ({err_type}): {err_str}")
        return None


def run_async_readonly(coro, timeout=15):
    """
    Run a read-only async coroutine WITHOUT the LLM lock.
    Use this for Neo4j queries that don't call Ollama — so they
    are never blocked by background entity extraction tasks.
    """
    global _async_loop, _loop_thread

    if _async_loop is None:
        _async_loop = asyncio.new_event_loop()
        _loop_thread = threading.Thread(
            target=_start_background_loop,
            args=(_async_loop,),
            daemon=True
        )
        _loop_thread.start()

    # NO lock — submit directly
    future = asyncio.run_coroutine_threadsafe(coro, _async_loop)
    try:
        return future.result(timeout=timeout)
    except Exception as e:
        err_str = str(e)
        if "Timeout" not in err_str:
            print(f"[Memory ReadOnly] {type(e).__name__}: {err_str}")
        return None


# ---------------------------------------------------------------------------
# PATIENT MEMORY CLASS
# ---------------------------------------------------------------------------
class PatientMemory:
    """
    Persistent graph-based memory for a single patient device.

    All data is scoped by group_id so each patient has completely
    isolated memory. Patient A's history never contaminates Patient B.

    Example usage:
        mem = PatientMemory("DCA632971FC3")

        # Store a notable event
        await mem.add_episode(
            "Patient's HR spiked to 125 after lunch. Non-critical — known pattern.",
            episode_type="baseline"
        )

        # Query before making a monitoring decision
        ctx = await mem.get_patient_context("Is HR 125 dangerous for this patient?")
        # Returns: "Patient Memory Context:\n- Patient HR 125 after lunch is normal..."
    """

    def __init__(self, device_id: str):
        self.device_id = device_id
        # group_id scopes all episodes to this specific patient
        self.group_id = f"patient_{device_id}"

    async def add_episode(self, content: str, episode_type: str = "observation") -> None:
        """
        Store an event as a natural-language episode in the memory graph.

        Args:
            content      : Descriptive text. Be specific — include vitals, location,
                           time context. Graphiti extracts entities from this text.
            episode_type : Category tag (observation, alert, baseline, meal, sleep, etc.)
        """
        graphiti = await get_graphiti()

        episode_name = f"{episode_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        await graphiti.add_episode(
            name=episode_name,
            episode_body=content,
            source_description=f"UTLMediCore sensor stream — Device {self.device_id}",
            group_id=self.group_id,
            reference_time=datetime.now(),
        )
        print(f"[Memory] Stored [{episode_type}] for {self.device_id}: {content[:60]}...")

    async def get_patient_context(self, query: str, limit: int = 10) -> str:
        """
        Retrieve patient memory context using a 2-tier strategy:

        Tier 1: graphiti.search() — semantic search over extracted EntityEdge facts.
                Returns rich, structured facts. Works once Graphiti LLM extraction completes.

        Tier 2: Direct Neo4j episode query — reads raw Episodic nodes content directly.
                Always works immediately, no LLM extraction needed.
                Used as fallback when Tier 1 returns empty or fails.

        Args:
            query : Question to search against (used for Tier 1 semantic search)
            limit : Max results per tier
        """
        # ── Tier 1: Graphiti semantic search (EntityEdge facts) ──────────────
        try:
            graphiti = await get_graphiti()
            results = await graphiti.search(
                query=query,
                group_ids=[self.group_id],
                num_results=limit,
            )
            if results:
                context_lines = [f"- {edge.fact}" for edge in results]
                context = (
                    "Patient Memory Context — extracted facts (from Graphiti knowledge graph):\n"
                    + "\n".join(context_lines)
                )
                print(f"[Memory Tier-1] {len(results)} facts retrieved for {self.device_id}")
                return context
        except Exception as e:
            print(f"[Memory Tier-1] graphiti.search() failed: {e}")

        # ── Tier 2: Direct Neo4j episode text query (always available) ───────
        try:
            import os
            from neo4j import AsyncGraphDatabase

            uri  = os.getenv("NEO4J_URI",      "bolt://localhost:7687")
            user = os.getenv("NEO4J_USER",     "neo4j")
            pw   = os.getenv("NEO4J_PASSWORD", "password")

            driver = AsyncGraphDatabase.driver(uri, auth=(user, pw))
            episodes = []
            async with driver.session() as s:
                # Get latest N episodes, sorted newest-first
                r = await s.run(
                    """
                    MATCH (e:Episodic)
                    WHERE e.group_id = $gid
                    RETURN e.name AS name,
                           e.content AS content,
                           e.valid_at AS ts
                    ORDER BY e.created_at DESC
                    LIMIT $lim
                    """,
                    gid=self.group_id,
                    lim=limit,
                )
                async for rec in r:
                    content = (rec["content"] or "").strip()
                    ts = str(rec["ts"] or "")[:16]
                    if content:
                        episodes.append(f"[{ts}] {content}")

            await driver.close()

            if episodes:
                context = (
                    f"Patient Episode History — {len(episodes)} recent records "
                    f"(direct from Neo4j, entity extraction still processing):\n"
                    + "\n\n".join(episodes)
                )
                print(f"[Memory Tier-2] {len(episodes)} episodes read directly for {self.device_id}")
                return context

        except Exception as e:
            print(f"[Memory Tier-2] Neo4j direct query failed: {e}")

        # ── Both tiers empty / failed ─────────────────────────────────────────
        return "No patient history available yet. This appears to be the first session."

    async def get_patient_episodes_direct(self, limit: int = 10, hours: int = 24) -> str:
        """
        Tier-2 fallback: Read raw Episodic nodes directly from Neo4j.
        Does NOT call Ollama — always fast, no lock contention.
        Sample episodes randomly within the requested timeframe so we don't just get the last 10 minutes.
        Returns episode texts as context string, or empty string if none found.
        """
        try:
            import os
            from neo4j import AsyncGraphDatabase

            uri  = os.getenv("NEO4J_URI",      "bolt://localhost:7687")
            user = os.getenv("NEO4J_USER",     "neo4j")
            pw   = os.getenv("NEO4J_PASSWORD", "password")

            driver = AsyncGraphDatabase.driver(uri, auth=(user, pw))
            episodes = []
            dur_start = f'PT{hours}H'
            
            # If hours>24 but not 168 (e.g. 48 for Yesterday), focus explicitly on the window [24h ago to 48h ago]
            if hours == 48:
                dur_end = 'PT24H'
            else:
                dur_end = 'PT0H'

            async with driver.session() as s:
                r = await s.run(
                    """
                    MATCH (e:Episodic)
                    WHERE e.group_id = $gid
                      AND e.created_at >= datetime() - duration($dur_start)
                      AND e.created_at <= datetime() - duration($dur_end)
                    WITH e, rand() AS r
                    ORDER BY r
                    LIMIT $lim
                    WITH e
                    ORDER BY e.created_at ASC
                    RETURN e.name    AS name,
                           e.content AS content,
                           e.valid_at AS ts
                    """,
                    gid=self.group_id,
                    lim=limit,
                    dur_start=dur_start,
                    dur_end=dur_end,
                )
                async for rec in r:
                    content = (rec["content"] or "").strip()
                    ts = str(rec["ts"] or "")[:16]
                    if content:
                        episodes.append(f"[{ts}] {content}")
            await driver.close()

            if episodes:
                print(f"[Memory Tier-2] {len(episodes)} episodes direct for {self.device_id}")
                return (
                    f"Patient Episode History — {len(episodes)} recent records:\n"
                    + "\n\n".join(episodes)
                )
        except Exception as e:
            print(f"[Memory Tier-2] Neo4j direct failed: {e}")
        return ""

    async def get_activity_summary(self, hours_back: int = 24) -> str:
        """
        Compute DURATION-BASED activity statistics from Neo4j episode timestamps.
        Groups consecutive same-posture/location snapshots and calculates:
        - Time spent in each posture (Prone, Sitting, Standing, Walking...)
        - Time spent in each area/room
        - First and last recorded times
        - Step count trends

        This enables the chatbot to answer 'how long' questions accurately.
        """
        try:
            import os
            from neo4j import AsyncGraphDatabase
            from datetime import timedelta

            uri  = os.getenv("NEO4J_URI",      "bolt://localhost:7687")
            user = os.getenv("NEO4J_USER",     "neo4j")
            pw   = os.getenv("NEO4J_PASSWORD", "password")

            driver = AsyncGraphDatabase.driver(uri, auth=(user, pw))
            episodes = []
            dur_start = f'PT{hours_back}H'
            
            # If hours_back>24 but not 168 (e.g. 48 for Yesterday+Today), we just query from "now - 48h" and include everything 
            # until "now". If we only wanted yesterday, we'd do dur_end='PT24H'. 
            # In reports, 48 hours is usually the full 48h.
            dur_end = 'PT0H'

            async with driver.session() as s:
                r = await s.run(
                    """
                    MATCH (e:Episodic)
                    WHERE e.group_id = $gid
                      AND e.created_at >= datetime() - duration($dur_start)
                      AND e.created_at <= datetime() - duration($dur_end)
                    RETURN e.content  AS content,
                           e.valid_at AS ts
                    ORDER BY e.created_at ASC
                    """,
                    gid=self.group_id,
                    dur_start=dur_start,
                    dur_end=dur_end,
                )
                async for rec in r:
                    content = (rec["content"] or "").strip()
                    ts_raw  = str(rec["ts"] or "")
                    if content and ts_raw:
                        # Parse timestamp
                        try:
                            ts_str = ts_raw.split("+")[0].split("000")[0].rstrip(".")
                            ts = datetime.fromisoformat(ts_str)
                        except Exception:
                            ts = None
                        # Extract posture and area from episode text
                        posture = "Unknown"
                        area    = "Unknown"
                        steps_n = 0
                        for line in content.split("."):
                            l = line.strip()
                            if "Activity/Posture:" in l:
                                posture = l.split("Activity/Posture:")[-1].strip()
                            elif "Location:" in l:
                                area = l.split("Location:")[-1].strip()
                            elif "Step count:" in l:
                                try:
                                    steps_n = int(l.split("Step count:")[-1].strip().split()[0])
                                except Exception:
                                    pass
                        episodes.append({"ts": ts, "posture": posture, "area": area, "steps": steps_n, "content": content[:120]})

            await driver.close()

            if not episodes:
                return ""

            # ── Compute duration per posture (group consecutive same-posture) ──
            posture_durations: dict[str, float] = {}  # posture → total minutes
            area_durations:    dict[str, float] = {}
            step_records = []

            for i in range(len(episodes) - 1):
                ep   = episodes[i]
                nxt  = episodes[i + 1]
                if ep["ts"] and nxt["ts"]:
                    delta_min = (nxt["ts"] - ep["ts"]).total_seconds() / 60
                    # Only count reasonable intervals (1s to 2h) to avoid gaps overnight
                    if 0 < delta_min <= 120:
                        p = ep["posture"]
                        a = ep["area"]
                        posture_durations[p] = posture_durations.get(p, 0) + delta_min
                        area_durations[a]    = area_durations.get(a, 0) + delta_min

                if ep["steps"] > 0:
                    step_records.append(ep["steps"])

            # ── Format output for LLM ──
            lines = [f"ACTIVITY DURATION SUMMARY for Patient {self.device_id}:"]
            lines.append(f"Based on {len(episodes)} recorded snapshots.\n")

            first_ts = next((e["ts"] for e in episodes if e["ts"]), None)
            last_ts  = next((e["ts"] for e in reversed(episodes) if e["ts"]), None)
            if first_ts and last_ts:
                span_h = (last_ts - first_ts).total_seconds() / 3600
                lines.append(f"Monitoring period: {first_ts.strftime('%Y-%m-%d %H:%M')} to {last_ts.strftime('%Y-%m-%d %H:%M')} ({span_h:.1f} hours total)\n")

            if posture_durations:
                lines.append("Time spent in each posture:")
                for posture, mins in sorted(posture_durations.items(), key=lambda x: -x[1]):
                    h, m = divmod(int(mins), 60)
                    label = f"  {posture}: {h}h {m}min" if h else f"  {posture}: {int(mins)} min"
                    lines.append(label)

            if area_durations:
                lines.append("\nTime spent in each location:")
                for area, mins in sorted(area_durations.items(), key=lambda x: -x[1]):
                    h, m = divmod(int(mins), 60)
                    label = f"  {area}: {h}h {m}min" if h else f"  {area}: {int(mins)} min"
                    lines.append(label)

            if step_records:
                avg_steps = sum(step_records) / len(step_records)
                max_steps = max(step_records)
                lines.append(f"\nStep count — avg: {int(avg_steps):,}, max recorded: {int(max_steps):,}")

            print(f"[Memory Summary] Generated activity summary for {self.device_id}")
            return "\n".join(lines)

        except Exception as e:
            print(f"[Memory Summary] Failed: {e}")
            return ""

    async def get_raw_history(self, hours_back: int) -> list:
        try:
            import os
            from neo4j import AsyncGraphDatabase

            uri  = os.getenv("NEO4J_URI",      "bolt://localhost:7687")
            user = os.getenv("NEO4J_USER",     "neo4j")
            pw   = os.getenv("NEO4J_PASSWORD", "password")

            driver = AsyncGraphDatabase.driver(uri, auth=(user, pw))
            episodes = []
            dur_start = f'PT{hours_back}H'
            dur_end = 'PT0H'

            async with driver.session() as s:
                r = await s.run(
                    """
                    MATCH (e:Episodic)
                    WHERE e.group_id = $gid
                      AND e.created_at >= datetime() - duration($dur_start)
                      AND e.created_at <= datetime() - duration($dur_end)
                    RETURN e.content  AS content,
                           e.valid_at AS ts
                    ORDER BY e.created_at ASC
                    """,
                    gid=self.group_id,
                    dur_start=dur_start,
                    dur_end=dur_end,
                )
                async for rec in r:
                    content = (rec["content"] or "").strip()
                    ts_raw  = str(rec["ts"] or "")
                    if content and ts_raw:
                        # Parse timestamp
                        try:
                            ts_str = ts_raw.split("+")[0].split("000")[0].rstrip(".")
                            ts = datetime.fromisoformat(ts_str)
                        except Exception:
                            ts = datetime.now()
                            
                        # Extract metrics
                        posture = "Unknown"
                        area = "Unknown"
                        steps_n = 0
                        hr = 0
                        spo2 = 0
                        
                        for line in content.split("."):
                            l = line.strip()
                            if "Activity/Posture:" in l:
                                posture = l.split("Activity/Posture:")[-1].strip()
                            elif "Location:" in l:
                                area = l.split("Location:")[-1].strip()
                            elif "Step count:" in l:
                                try: steps_n = int(l.split("Step count:")[-1].strip().split()[0])
                                except: pass
                            elif "Heart Rate:" in l:
                                try: hr = int(l.split("Heart Rate:")[-1].strip().split()[0])
                                except: pass
                            elif "Blood O2:" in l:
                                try: spo2 = int(l.split("Blood O2:")[-1].strip().replace('%', '').split()[0])
                                except: pass
                                
                        episodes.append({
                            'timestamp': ts.isoformat(),
                            'HR': hr,
                            'Blood_oxygen': spo2,
                            'Posture_state': posture,
                            'Area': area,
                            'Step': steps_n
                        })

            await driver.close()
            return episodes
        except Exception as e:
            print(f"[Memory Raw History] Neo4j fetch failed: {e}")
            return []



    async def get_episodes_by_time_range(
        self,
        center_hour: int,
        center_minute: int = 0,
        window_minutes: int = 45,
        date_str: Optional[str] = None,
        limit: int = 30,
    ) -> str:
        """
        Query Neo4j for episodes near a specific time of day.
        Uses Neo4j DateTime .hour / .minute / .day attributes (not string compare).

        Args:
            center_hour    : Hour to look up (0-23), e.g. 8 for 8AM
            center_minute  : Minute within hour
            window_minutes : ±window around center time (default 45 min)
            date_str       : 'YYYY-MM-DD' to restrict to one day; None = all dates
            limit          : Max records to return
        """
        try:
            import os
            from neo4j import AsyncGraphDatabase
            from datetime import timedelta

            uri  = os.getenv("NEO4J_URI",      "bolt://localhost:7687")
            user = os.getenv("NEO4J_USER",     "neo4j")
            pw   = os.getenv("NEO4J_PASSWORD", "password")

            # Compute start/end as (hour, minute) pairs, handling midnight wrap
            center_total = center_hour * 60 + center_minute
            start_total  = center_total - window_minutes
            end_total    = center_total + window_minutes

            start_h, start_m = divmod(max(start_total, 0), 60)
            end_h,   end_m   = divmod(min(end_total, 23 * 60 + 59), 60)

            # Optionally scope to a specific date
            date_filter = ""
            date_params: dict = {}
            if date_str:
                try:
                    from datetime import date as _date
                    d = datetime.strptime(date_str, "%Y-%m-%d").date()
                    date_filter = "AND e.valid_at.year = $yr AND e.valid_at.month = $mo AND e.valid_at.day = $dy"
                    date_params = {"yr": d.year, "mo": d.month, "dy": d.day}
                except Exception:
                    pass

            # Convert start/end minutes-of-day to comparable integer  
            # (hour*60 + minute) for easy range filter in Cypher
            cypher = f"""
                MATCH (e:Episodic)
                WHERE e.group_id = $gid
                  AND (e.valid_at.hour * 60 + e.valid_at.minute) >= $start_mins
                  AND (e.valid_at.hour * 60 + e.valid_at.minute) <= $end_mins
                  {date_filter}
                RETURN toString(e.valid_at) AS ts_str,
                       e.content            AS content
                ORDER BY e.valid_at ASC
                LIMIT $lim
            """
            params = {
                "gid":        self.group_id,
                "start_mins": start_h * 60 + start_m,
                "end_mins":   end_h   * 60 + end_m,
                "lim":        limit,
                **date_params,
            }

            driver = AsyncGraphDatabase.driver(uri, auth=(user, pw))
            episodes = []
            async with driver.session() as s:
                r = await s.run(cypher, **params)
                async for rec in r:
                    content  = (rec["content"] or "").strip()
                    ts_label = (rec["ts_str"] or "")[:16]
                    if content:
                        episodes.append(f"[{ts_label}] {content}")

            await driver.close()

            if not episodes:
                msg = f"[Memory TimeRange] No episodes found at {center_hour:02d}:{center_minute:02d} (±{window_minutes}min) for {self.device_id}"
                print(msg)
                return ""

            date_label = date_str or "any date"
            header = (
                f"Timeline records for {self.device_id} "
                f"around {center_hour:02d}:{center_minute:02d} ±{window_minutes}min"
                f" [{date_label}] — {len(episodes)} records:\n"
            )
            print(f"[Memory TimeRange] {len(episodes)} records found around {center_hour:02d}:{center_minute:02d} for {self.device_id}")
            return header + "\n".join(episodes)

        except Exception as e:
            print(f"[Memory TimeRange] Failed: {e}")
            return ""



    async def store_alert(self, alert_data: dict) -> None:

        """
        Persist an alert into memory so future agents remember past emergencies.

        Args:
            alert_data : Dict with keys: severity, message, anomalies, device_id
        """
        severity = alert_data.get("severity", "UNKNOWN")
        message = alert_data.get("message", "Alert generated")
        anomalies = alert_data.get("anomalies", [])
        anomaly_text = ", ".join(anomalies) if anomalies else "unspecified anomalies"

        episode_text = (
            f"EMERGENCY ALERT recorded at {datetime.now().strftime('%H:%M on %A %d %B %Y')}. "
            f"Severity: {severity}. "
            f"Detected: {anomaly_text}. "
            f"Full message: {message}."
        )
        await self.add_episode(episode_text, episode_type="alert")

    async def store_sensor_snapshot(
        self,
        data: dict,
        posture_map: Optional[dict] = None,
        area_map: Optional[dict] = None,
    ) -> None:
        """
        Convert a raw sensor reading dict into a human-readable episode.

        Called every N readings (not every single reading — too noisy).
        Only stores if the reading is notable (abnormal vitals or notable posture).

        Args:
            data        : Raw sensor dict with HR, Blood_oxygen, Posture_state, Area keys
            posture_map : Optional override for posture code→text mapping
            area_map    : Optional override for area code→text mapping
        """
        posture_map = posture_map or _POSTURE_MAP
        area_map = area_map or _AREA_MAP

        hr = int(data.get("HR", 0))
        spo2 = int(data.get("Blood_oxygen", 0))
        posture_val = int(data.get("Posture_state", 0))
        area_val = int(data.get("Area", data.get("Lokasi", 0)))
        steps = int(data.get("Step", 0))

        posture_txt = posture_map.get(posture_val, "Unknown")
        area_txt = area_map.get(area_val, "Unknown Area")
        now = datetime.now()
        timestamp_full = now.strftime("%H:%M on %A, %d %B %Y")
        timestamp_short = now.strftime("%Y-%m-%d %H:%M")

        # Decide episode type
        is_fall = posture_val == 5
        is_abnormal_hr = hr > 0 and (hr > 110 or hr < 45)
        is_low_oxygen = 0 < spo2 < 90
        is_tachycardia = hr > 100
        is_bradycardia = hr < 50

        if is_fall:
            episode_type = "critical_fall"
            severity_label = "CRITICAL — FALL DETECTED"
        elif is_abnormal_hr and is_low_oxygen:
            episode_type = "critical_vitals"
            severity_label = "CRITICAL — Simultaneous HR and SpO2 abnormality"
        elif is_low_oxygen:
            episode_type = "low_oxygen"
            severity_label = "WARNING — Low Blood Oxygen (possible hypoxia)"
        elif is_tachycardia:
            episode_type = "abnormal_hr"
            severity_label = "WARNING — Tachycardia (elevated heart rate)"
        elif is_bradycardia:
            episode_type = "abnormal_hr"
            severity_label = "WARNING — Bradycardia (low heart rate)"
        else:
            episode_type = "routine_observation"
            severity_label = "Normal — all vitals within safe parameters"

        # HR clinical interpretation
        if hr > 110:
            hr_note = f"{hr} bpm (elevated, above normal range of 60-100 bpm)"
        elif hr < 45:
            hr_note = f"{hr} bpm (dangerously low, below normal range of 60-100 bpm)"
        elif hr > 100:
            hr_note = f"{hr} bpm (mildly elevated, normal range is 60-100 bpm)"
        elif hr < 60:
            hr_note = f"{hr} bpm (slightly low, normal range is 60-100 bpm)"
        else:
            hr_note = f"{hr} bpm (normal range)"

        # SpO2 clinical interpretation
        if spo2 < 90:
            spo2_note = f"{spo2}% (critically low — hypoxia risk; normal is 95-100%)"
        elif spo2 < 95:
            spo2_note = f"{spo2}% (mildly low; normal is 95-100%)"
        else:
            spo2_note = f"{spo2}% (normal)"

        # Steps interpretation
        if steps > 5000:
            steps_note = f"{steps} steps (high activity day)"
        elif steps > 1000:
            steps_note = f"{steps} steps (moderate activity)"
        else:
            steps_note = f"{steps} steps (low activity)"

        # Time-of-day clinical context
        hour = now.hour
        if 5 <= hour < 12:
            time_context = "morning"
        elif 12 <= hour < 17:
            time_context = "afternoon"
        elif 17 <= hour < 21:
            time_context = "evening"
        else:
            time_context = "night"

        # Posture risk context
        posture_risk = ""
        if posture_val == 6:  # Prone
            posture_risk = " (prone position increases respiratory risk)"
        elif posture_val == 3 and hour >= 22 or hour < 6:  # Lying down at night
            posture_risk = " (nighttime rest)"
        elif posture_val == 8:  # Walking
            posture_risk = " (active movement)"

        # Build rich, entity-dense episode text
        episode_text = (
            f"[{severity_label}] "
            f"Patient {self.device_id} monitoring record at {timestamp_full} ({timestamp_short}). "
            f"Time of day: {time_context}. "
            f"Location: {area_txt}. "
            f"Activity/Posture: {posture_txt}{posture_risk}. "
            f"Heart Rate: {hr_note}. "
            f"Blood Oxygen (SpO2): {spo2_note}. "
            f"Step count: {steps_note}. "
        )

        # Add clinical summary sentence for better entity extraction
        if is_fall:
            episode_text += (
                f"Patient {self.device_id} experienced a fall event at {area_txt}. "
                f"Immediate assessment required. "
                f"Heart Rate at time of fall was {hr} bpm, SpO2 was {spo2}%."
            )
        elif is_low_oxygen and is_abnormal_hr:
            episode_text += (
                f"Patient {self.device_id} showed simultaneous respiratory and cardiac distress "
                f"in {area_txt}. HR {hr} bpm and SpO2 {spo2}% both outside safe ranges."
            )
        elif is_low_oxygen:
            episode_text += (
                f"Patient {self.device_id} had low blood oxygen of {spo2}% "
                f"while {posture_txt.lower()} in {area_txt}. Monitor breathing closely."
            )
        elif is_tachycardia:
            episode_text += (
                f"Patient {self.device_id} had elevated heart rate ({hr} bpm) "
                f"while {posture_txt.lower()} in {area_txt}. "
                f"SpO2 remained {spo2}%. May indicate exertion, stress, or cardiac event."
            )
        elif is_bradycardia:
            episode_text += (
                f"Patient {self.device_id} had unusually low heart rate ({hr} bpm) "
                f"while {posture_txt.lower()} in {area_txt}."
            )
        else:
            episode_text += (
                f"Patient {self.device_id} was {posture_txt.lower()} in {area_txt} "
                f"with stable vitals. HR {hr} bpm and SpO2 {spo2}% within normal range."
            )

        await self.add_episode(episode_text, episode_type=episode_type)


    async def store_baseline(self, description: str) -> None:
        """
        Explicitly store a known patient baseline.
        Use this when you've confirmed something is normal for a specific patient.

        Example:
            await mem.store_baseline(
                "Patient DCA typically has HR 115-130 after meals around noon. "
                "This is their personal normal and should NOT trigger alerts."
            )
        """
        episode_text = (
            f"PATIENT BASELINE NOTE recorded at "
            f"{datetime.now().strftime('%d %B %Y')}: {description}"
        )
        await self.add_episode(episode_text, episode_type="baseline")
