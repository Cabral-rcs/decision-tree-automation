# responses_controller.py - Controller para respostas
from fastapi import Request, Response
from backend.models.responses_model import add_response, get_all_responses

async def receive_response(request: Request):
    data = await request.json()
    # Espera-se que data contenha: user_id, pergunta, resposta, timestamp
    add_response(data)
    return {"status": "ok"}

async def list_responses():
    responses = get_all_responses()
    return responses 