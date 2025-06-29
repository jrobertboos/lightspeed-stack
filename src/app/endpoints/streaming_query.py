"""Handler for REST API call to provide answer to streaming query."""

import json
import logging
from typing import Any, AsyncIterator

from llama_stack_client.lib.agents.agent import AsyncAgent  # type: ignore
from llama_stack_client import AsyncLlamaStackClient  # type: ignore
from llama_stack_client.types import UserMessage  # type: ignore

from fastapi import APIRouter, Request, Depends
from fastapi.responses import StreamingResponse

from client import get_llama_stack_client
from configuration import configuration
from models.requests import QueryRequest
import constants
from utils.auth import auth_dependency
from utils.common import retrieve_user_id


from app.endpoints.query import (
    is_transcripts_enabled,
    retrieve_conversation_id,
    store_transcript,
    select_model_id,
    validate_attachments_metadata,
)

logger = logging.getLogger("app.endpoints.handlers")
router = APIRouter(tags=["query"])


def format_stream_data(d: dict) -> str:
    """Format outbound data in the Event Stream Format."""
    data = json.dumps(d)
    return f"data: {data}\n\n"


def stream_start_event(conversation_id: str) -> str:
    """Yield the start of the data stream.

    Args:
        conversation_id: The conversation ID (UUID).
    """
    return format_stream_data(
        {
            "event": "start",
            "data": {
                "conversation_id": conversation_id,
            },
        }
    )


def stream_end_event() -> str:
    """Yield the end of the data stream."""
    return format_stream_data(
        {
            "event": "end",
            "data": {
                "referenced_documents": None,  # TODO(jboos): implement referenced documents
                "truncated": None,  # TODO(jboos): implement truncated
                "input_tokens": 0,  # TODO(jboos): implement input tokens
                "output_tokens": 0,  # TODO(jboos): implement output tokens
            },
            "available_quotas": {},  # TODO(jboos): implement available quotas
        }
    )


@router.post("/streaming_query")
async def streaming_query_endpoint_handler(
    _request: Request,
    query_request: QueryRequest,
    auth: Any = Depends(auth_dependency),
) -> StreamingResponse:
    """Handle request to the /query endpoint."""
    llama_stack_config = configuration.llama_stack_configuration
    logger.info("LLama stack config: %s", llama_stack_config)
    client = get_llama_stack_client(llama_stack_config, async_client=True)
    model_id = select_model_id(await client.models.list(), query_request)
    conversation_id = retrieve_conversation_id(query_request)
    response = await retrieve_response(client, model_id, query_request)

    async def response_generator(turn_response: Any) -> AsyncIterator[str]:
        """Generate SSE formatted streaming response."""
        token_id = 0
        complete_response = ""

        # Send start event
        yield stream_start_event(conversation_id)

        async for res in turn_response:
            if hasattr(res.event, "payload"):
                if res.event.payload.event_type == "step_progress":
                    if hasattr(res.event.payload.delta, "text"):
                        text = res.event.payload.delta.text
                        yield format_stream_data(
                            {"event": "token", "data": {"id": token_id, "token": text}}
                        )
                        token_id += 1
                        complete_response += text

        yield stream_end_event()

        if not is_transcripts_enabled():
            logger.debug("Transcript collection is disabled in the configuration")
        else:
            store_transcript(
                user_id=retrieve_user_id(auth),
                conversation_id=conversation_id,
                query_is_valid=True,  # TODO(lucasagomes): implement as part of query validation
                query=query_request.query,
                query_request=query_request,
                response=complete_response,
                rag_chunks=[],  # TODO(lucasagomes): implement rag_chunks
                truncated=False,  # TODO(lucasagomes): implement truncation as part of quota work
                attachments=query_request.attachments or [],
            )

    return StreamingResponse(response_generator(response))


async def retrieve_response(
    client: AsyncLlamaStackClient, model_id: str, query_request: QueryRequest
) -> Any:
    """Retrieve response from LLMs and agents."""
    available_shields = [shield.identifier for shield in await client.shields.list()]
    if not available_shields:
        logger.info("No available shields. Disabling safety")
    else:
        logger.info("Available shields found: %s", available_shields)

    # use system prompt from request or default one
    system_prompt = (
        query_request.system_prompt
        if query_request.system_prompt
        else constants.DEFAULT_SYSTEM_PROMPT
    )
    logger.debug("Using system prompt: %s", system_prompt)

    # TODO(lucasagomes): redact attachments content before sending to LLM
    # if attachments are provided, validate them
    if query_request.attachments:
        validate_attachments_metadata(query_request.attachments)

    agent = AsyncAgent(
        client,
        model=model_id,
        instructions=system_prompt,
        input_shields=available_shields if available_shields else [],
        tools=[],
    )
    session_id = await agent.create_session("chat_session")
    logger.debug("Session ID: %s", session_id)
    response = await agent.create_turn(
        messages=[UserMessage(role="user", content=query_request.query)],
        session_id=session_id,
        documents=query_request.get_documents(),
        stream=True,
    )

    return response
