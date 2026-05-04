import json
import uuid
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from .models import ChatSession, ChatMessage

SESSION_MESSAGE_LIMIT = 20


class ChatPageView(TemplateView):
    """Full-page chat interface at /chat/."""
    template_name = 'chatbot/chat.html'


@require_POST
def chat_api(request):
    """
    POST /chat/api/
    Body: {"message": "...", "session_id": "<uuid or null>"}
    Returns: {"reply": "...", "session_id": "<uuid>"}

    Creates or resumes a ChatSession, enforces the 20-message rate limit,
    runs the RAG chain, and persists both sides of the exchange.
    """
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    user_message = payload.get('message', '').strip()
    if not user_message:
        return JsonResponse({'error': 'Empty message'}, status=400)

    raw_session_id = payload.get('session_id')

    # Resolve or create session
    session = None
    if raw_session_id:
        try:
            session_uuid = uuid.UUID(str(raw_session_id))
            session = ChatSession.objects.filter(session_id=session_uuid).first()
        except (ValueError, AttributeError):
            pass

    if session is None:
        session = ChatSession.objects.create()

    # Rate limiting: count only user messages toward the limit
    user_msg_count = session.messages.filter(role='user').count()
    if user_msg_count >= SESSION_MESSAGE_LIMIT:
        return JsonResponse(
            {'error': 'Message limit reached for this session. Please refresh to start a new chat.'},
            status=429,
        )

    # Persist the user message
    ChatMessage.objects.create(session=session, role='user', content=user_message)

    # Run RAG chain — import here to avoid circular issues and allow lazy init
    try:
        from .rag.chain import ask
        reply = ask(user_message)
    except Exception as exc:
        # Surface a friendly error rather than 500-ing the user
        reply = f"I'm having trouble connecting right now. Please try again in a moment. ({type(exc).__name__})"

    # Persist the assistant reply
    ChatMessage.objects.create(session=session, role='assistant', content=reply)

    return JsonResponse({'reply': reply, 'session_id': str(session.session_id)})
