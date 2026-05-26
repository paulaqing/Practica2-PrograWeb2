import socketio
from datetime import datetime
from .middleware.auth import verify_jwt_token
from .models.user import get_all_users
from .models.message import get_room_messages, save_message, cleanup_messages

# Crear servidor Socket.io asíncrono compatible con ASGI
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
socket_app = socketio.ASGIApp(sio)

@sio.event
async def connect(sid, environ, auth):
    """
    Controlador de conexión del WebSocket.
    Valida el token JWT enviado en el diccionario 'auth' del cliente.
    """
    if not auth or 'token' not in auth:
        print("🔴 Conexión rechazada: Token no proporcionado")
        return False
    
    token = auth['token']
    payload = verify_jwt_token(token)
    if not payload:
        print("🔴 Conexión rechazada: Token inválido")
        return False
        
    # Guardar los datos del usuario decodificados en la sesión del socket
    await sio.save_session(sid, {'user': payload})
    print(f"🟢 {payload.get('username')} ({payload.get('role')}) conectado al chat (sid: {sid})")
    return True

@sio.event
async def disconnect(sid):
    """
    Controlador para cuando un cliente se desconecta.
    """
    session = await sio.get_session(sid)
    user = session.get('user', {}) if session else {}
    username = user.get('username', 'Anónimo')
    print(f"🔴 {username} desconectado del chat (sid: {sid})")

@sio.event
async def getAvailableUsers(sid):
    """
    Obtiene todos los usuarios de la base de datos excepto el propio usuario
    conectado, devolviendo sus nombres y roles.
    """
    session = await sio.get_session(sid)
    user = session.get('user', {}) if session else {}
    username = user.get('username', 'Anónimo')
    
    try:
        users = await get_all_users()
        filtered_users = [
            {"username": u["username"], "role": u["role"]}
            for u in users if u["username"] != username
        ]
        await sio.emit('availableUsers', filtered_users, room=sid)
    except Exception as e:
        print(f"⚠️ Error al obtener usuarios disponibles: {e}")

@sio.event
async def joinRoom(sid, room):
    """
    Permite a un usuario unirse a una sala específica del chat privado y
    carga el historial de los últimos 50 mensajes de esa sala.
    """
    await sio.enter_room(sid, room)
    session = await sio.get_session(sid)
    if session is not None:
        session['currentRoom'] = room
        await sio.save_session(sid, session)
    
    try:
        # Cargar los últimos 50 mensajes
        history = await get_room_messages(room, limit=50)
        history_formatted = []
        for m in history:
            ts = m.get("timestamp")
            ts_str = "Ahora"
            if isinstance(ts, datetime):
                # Formatear la fecha en formato legible de hora
                ts_str = ts.strftime("%H:%M:%S")
            
            history_formatted.append({
                "name": m.get("sender"),
                "msg": m.get("message"),
                "timestamp": ts_str
            })
        await sio.emit('messageHistory', history_formatted, room=sid)
    except Exception as e:
        print(f"⚠️ Error al cargar historial de chat de la sala {room}: {e}")

@sio.event
async def chatmessage(sid, data):
    """
    Recibe un mensaje de chat enviado por un cliente, lo persiste en MongoDB,
    realiza la limpieza de mensajes excedentes y retransmite a toda la sala.
    """
    if not data or 'message' not in data or 'room' not in data:
        return
        
    session = await sio.get_session(sid)
    user = session.get('user', {}) if session else {}
    username = user.get('username', 'Anónimo')
    
    room = data['room']
    message_text = data['message']
    
    # Obtener hora actual formateada
    ts_str = datetime.now().strftime("%H:%M:%S")
    
    message_data = {
        "name": username,
        "msg": message_text,
        "timestamp": ts_str
    }
    
    try:
        # Guardar en base de datos
        await save_message(room, username, message_text)
        # Limpieza de historial para mantener solo los últimos 50 mensajes de esta sala
        await cleanup_messages(room, max_messages=50)
    except Exception as e:
        print(f"⚠️ Error al persistir mensaje de chat: {e}")
        
    # Retransmitir a todos en la sala del chat
    await sio.emit('chatmessage', message_data, room=room)
