"""
DirectNeo4jWriter: Real-time structured vitals writer for UTLMediCore.
======================================================================

Menulis data sensor langsung ke Neo4j TANPA LLM — < 1 detik per write.
Digunakan untuk real-time vitals stream (setiap 3 menit).

Schema Node:
  (:Patient  {id, device_id})
  (:VitalReading  {hr, spo2, steps, posture, area, kcal, condition,
                   timestamp_local, timestamp_utc, valid_at})
  (:AlertEvent    {type, severity, message, timestamp_local, timestamp_utc})
  (:PostureChange {from_posture, to_posture, timestamp_local})

Relationships:
  (Patient)-[:HAD_READING]->(VitalReading)
  (Patient)-[:HAD_ALERT]->(AlertEvent)
  (Patient)-[:HAD_POSTURE_CHANGE]->(PostureChange)
"""

import os
from datetime import datetime, timezone

# ── Lazy import — connector hanya di-load saat pertama dipakai ────────────────
_driver = None

def _get_driver():
    global _driver
    if _driver is None:
        from neo4j import GraphDatabase
        uri  = os.getenv("NEO4J_URI",      "bolt://localhost:7687")
        user = os.getenv("NEO4J_USER",     "neo4j")
        pw   = os.getenv("NEO4J_PASSWORD", "password")
        _driver = GraphDatabase.driver(uri, auth=(user, pw))
        print(f"[DirectNeo4j] Connected to {uri}")
    return _driver


def write_vital_reading(device_id: str, data: dict) -> bool:
    """
    Tulis satu snapshot vital ke Neo4j langsung (tanpa LLM).

    Args:
        device_id: e.g. "C5945F0F59FB_D612D9000180"
        data: dict dengan key: hr, spo2, steps, posture, posture_label,
              area_label, kcal, condition, timestamp_local (str)

    Returns:
        True jika berhasil, False jika error
    """
    try:
        driver = _get_driver()
        ts_local = data.get("timestamp_local", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        # Prioritaskan timestamp_utc bawaan data dari memory agent
        now_utc = data.get("timestamp_utc", datetime.now(timezone.utc).isoformat())

        with driver.session() as session:
            session.run(
                """
                MERGE (p:Patient {device_id: $device_id})
                ON CREATE SET p.id = $device_id, p.created_at = $utc


                CREATE (v:VitalReading {
                    hr:              $hr,
                    spo2:            $spo2,
                    steps:           $steps,
                    posture:         $posture,
                    posture_label:   $posture_label,
                    area_label:      $area_label,
                    kcal:            $kcal,
                    condition:       $condition,
                    timestamp_local: $ts_local,
                    timestamp_utc:   $utc
                })
                CREATE (p)-[:HAD_READING]->(v)
                """,
                device_id    = device_id,
                hr           = data.get("hr", 0),
                spo2         = data.get("spo2", 0),
                steps        = data.get("steps", 0),
                posture      = data.get("posture", 0),
                posture_label= data.get("posture_label", "Unknown"),
                area_label   = data.get("area_label", "Unknown Area"),
                kcal         = data.get("kcal", 0),
                condition    = data.get("condition", "normal"),
                ts_local     = ts_local,
                utc          = now_utc,
            )
        print(f"[DirectNeo4j] ✅ VitalReading saved — {device_id} | HR:{data.get('hr')} SpO2:{data.get('spo2')} | {ts_local}")
        return True

    except Exception as e:
        print(f"[DirectNeo4j] ❌ write_vital_reading failed: {e}")
        return False


def write_alert_event(device_id: str, alert_type: str, severity: str, message: str) -> bool:
    """
    Tulis alert event ke Neo4j (bradycardia, hypoxia, fall, dll).

    Args:
        device_id: patient device ID
        alert_type: e.g. "bradycardia", "hypoxia", "fall_detected"
        severity:   "warning" | "critical"
        message:    human readable alert text
    """
    try:
        driver = _get_driver()
        now_utc   = datetime.now(timezone.utc).isoformat()
        ts_local  = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with driver.session() as session:
            session.run(
                """
                MERGE (p:Patient {device_id: $device_id})
                ON CREATE SET p.id = $device_id, p.created_at = $utc

                CREATE (a:AlertEvent {
                    alert_type:      $alert_type,
                    severity:        $severity,
                    message:         $message,
                    timestamp_local: $ts_local,
                    timestamp_utc:   $utc
                })
                CREATE (p)-[:HAD_ALERT]->(a)
                """,
                device_id  = device_id,
                alert_type = alert_type,
                severity   = severity,
                message    = message,
                ts_local   = ts_local,
                utc        = now_utc,
            )
        print(f"[DirectNeo4j] 🚨 AlertEvent saved — {device_id} | {alert_type} [{severity}]")
        return True

    except Exception as e:
        print(f"[DirectNeo4j] ❌ write_alert_event failed: {e}")
        return False


def write_posture_change(device_id: str, from_posture: str, to_posture: str) -> bool:
    """
    Catat perubahan postur pasien ke Neo4j.
    """
    try:
        driver = _get_driver()
        ts_local = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        now_utc  = datetime.now(timezone.utc).isoformat()

        with driver.session() as session:
            session.run(
                """
                MERGE (p:Patient {device_id: $device_id})
                ON CREATE SET p.id = $device_id

                CREATE (pc:PostureChange {
                    from_posture:    $from_posture,
                    to_posture:      $to_posture,
                    timestamp_local: $ts_local,
                    timestamp_utc:   $utc
                })
                CREATE (p)-[:HAD_POSTURE_CHANGE]->(pc)
                """,
                device_id    = device_id,
                from_posture = from_posture,
                to_posture   = to_posture,
                ts_local     = ts_local,
                utc          = now_utc,
            )
        print(f"[DirectNeo4j] 🔄 PostureChange saved — {device_id} | {from_posture} → {to_posture}")
        return True

    except Exception as e:
        print(f"[DirectNeo4j] ❌ write_posture_change failed: {e}")
        return False


def close():
    """Tutup koneksi Neo4j saat server shutdown."""
    global _driver
    if _driver:
        _driver.close()
        _driver = None
