## query neo4j penting

MATCH (e:Episodic)-[r]->(any_entity)
WHERE e.group_id = "patient_C5945F0F59FB_D612D9000180"
RETURN e.created_at AS Waktu_Dibuat, any_entity.name AS Entitas_Ditemukan
ORDER BY e.created_at DESC
LIMIT 50


MATCH (e:Episodic)-[r]->(any_entity)
WHERE e.group_id = "patient_C5945F0F59FB_D612D9000180"
RETURN e.created_at AS Waktu_Dibuat, any_entity.name AS Entitas
ORDER BY e.created_at DESC
LIMIT 100


MATCH (e:Episodic)
WHERE e.group_id = "patient_C5945F0F59FB_D612D9000180"
RETURN e.created_at AS Waktu, e.content AS Deskripsi
ORDER BY e.created_at DESC
LIMIT 50


MATCH (p:Patient {device_id: "C5945F0F59FB_D612D9000180"})-[:HAD_READING]->(v:VitalReading)
RETURN v.timestamp_local, v.hr, v.spo2, v.posture_label
ORDER BY v.timestamp_utc DESC
LIMIT 1500
