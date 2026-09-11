from __future__ import annotations

import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.engine import TICK_SECONDS, service

router = APIRouter()


@router.websocket("/ws/worlds/{world_id}")
async def world_socket(websocket: WebSocket, world_id: int) -> None:
    await websocket.accept()
    try:
        while True:
            try:
                payload = service.live_for(world_id)
            except KeyError:
                await websocket.close(code=1008)
                return
            await websocket.send_json(payload)
            try:
                await asyncio.wait_for(websocket.receive_text(), timeout=TICK_SECONDS)
            except TimeoutError:
                continue
            except WebSocketDisconnect:
                return
    except WebSocketDisconnect:
        return
