import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.models.conversation import Conversation, ConversationMessage


async def create_conversation(db: AsyncSession, organization_id: uuid.UUID, user_id: uuid.UUID) -> Conversation:
    """Start a new conversation session."""
    conversation = Conversation(organization_id=organization_id, user_id=user_id)
    db.add(conversation)
    await db.commit()
    await db.refresh(conversation)
    return conversation


async def get_conversation(db: AsyncSession, organization_id: uuid.UUID, conversation_id: uuid.UUID) -> Conversation:
    """Retrieve a conversation, scoped to the requesting organization."""
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.organization_id == organization_id,
        )
    )
    conversation = result.scalar_one_or_none()
    if conversation is None:
        raise NotFoundException("Conversation not found")
    return conversation


async def add_message(db: AsyncSession, conversation_id: uuid.UUID, role: str, content: str) -> ConversationMessage:
    """Append a message (user or assistant) to a conversation."""
    message = ConversationMessage(conversation_id=conversation_id, role=role, content=content)
    db.add(message)
    await db.commit()
    await db.refresh(message)
    return message


async def get_conversation_history(
    db: AsyncSession, organization_id: uuid.UUID, conversation_id: uuid.UUID, max_messages: int = 10
) -> list[ConversationMessage]:
    """Retrieve the most recent messages in a conversation, oldest first.

    Limiting to max_messages keeps the LLM prompt from growing unbounded
    as conversations get longer — older context naturally falls off.
    """
    await get_conversation(db, organization_id, conversation_id)  # validates access

    result = await db.execute(
        select(ConversationMessage)
        .where(ConversationMessage.conversation_id == conversation_id)
        .order_by(ConversationMessage.created_at.desc())
        .limit(max_messages)
    )
    messages = list(result.scalars().all())
    return list(reversed(messages))


def format_history_for_prompt(messages: list[ConversationMessage]) -> str:
    """Format prior conversation turns into a readable block for the LLM prompt."""
    if not messages:
        return ""

    lines = []
    for message in messages:
        speaker = "Employee" if message.role == "user" else "Assistant"
        lines.append(f"{speaker}: {message.content}")

    return "Previous conversation:\n" + "\n".join(lines) + "\n\n"