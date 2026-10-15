
from contextvars import ContextVar, Token


_req_context_var = ContextVar("request_id", default="")

def set_req_id(req_id:str) -> Token:
    token = _req_context_var.set(req_id)
    return token

def get_req_id() -> str:
    return _req_context_var.get()

def reset_req_id(token: Token):
    _req_context_var.reset(token)