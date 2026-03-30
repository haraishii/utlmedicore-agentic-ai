import asyncio
from memory.patient_memory import PatientMemory
import datetime

async def test_save():
    mem = PatientMemory('C5945F0F59FB_D612D9000180')
    await mem.add_episode("User just ate a banana", "meal", datetime.datetime.now())

asyncio.run(test_save())
