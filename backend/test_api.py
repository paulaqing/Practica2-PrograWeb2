import urllib.request
import urllib.parse
import json

BASE_URL = "http://localhost:3000"

def make_request(path, method="GET", data=None, token=None):
    url = f"{BASE_URL}{path}"
    headers = {
        "Content-Type": "application/json"
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
        
    req_data = None
    if data:
        req_data = json.dumps(data).encode("utf-8")
        
    req = urllib.request.Request(url, data=req_data, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req) as response:
            resp_body = response.read().decode("utf-8")
            return response.status, json.loads(resp_body) if resp_body else None
    except urllib.error.HTTPError as e:
        resp_body = e.read().decode("utf-8")
        try:
            err_json = json.loads(resp_body)
        except Exception:
            err_json = resp_body
        return e.code, err_json
    except Exception as ex:
        return 999, str(ex)

def run_tests():
    print("Iniciando pruebas automatizadas del nuevo backend FastAPI...")
    
    # 1. Test Root
    print("\n1. Probando GET / (Verificar estado del servidor)")
    status, body = make_request("/")
    assert status == 200, f"Error: {status} - {body}"
    print(f"   [OK] Servidor en linea: {body.get('message')}")
    
    # Generar usuario aleatorio para pruebas
    import time
    username = f"tester_{int(time.time())}"
    password = "password123"
    
    # 2. Test Registro
    print(f"\n2. Probando POST /register (Usuario: {username})")
    reg_data = {
        "username": username,
        "password": password
    }
    status, body = make_request("/register", method="POST", data=reg_data)
    assert status == 200, f"Error: {status} - {body}"
    print(f"   [OK] Registro exitoso: {body.get('message')}")
    
    # 3. Test Login
    print(f"\n3. Probando POST /login con las credenciales creadas")
    login_data = {
        "username": username,
        "password": password
    }
    status, body = make_request("/login", method="POST", data=login_data)
    assert status == 200, f"Error: {status} - {body}"
    token = body.get("token")
    assert token is not None, "Error: No se recibio el token"
    print(f"   [OK] Login exitoso! Token obtenido.")
    
    # 4. Test Listar Productos
    print("\n4. Probando GET /api/products (Listar productos de cafeteria)")
    status, body = make_request("/api/products", token=token)
    assert status == 200, f"Error: {status} - {body}"
    assert isinstance(body, list), "Error: Se esperaba una lista de productos"
    print(f"   [OK] Productos obtenidos: {len(body)} productos encontrados.")
    if len(body) > 0:
        first_product = body[0]
        print(f"        -> Ejemplo de producto: '{first_product.get('name')}' a {first_product.get('price')} euros.")
        product_id = first_product.get("id") or first_product.get("_id")
    else:
        product_id = None
        
    # 5. Test Carrito (Añadir al carrito)
    if product_id:
        print(f"\n5. Probando POST /api/cart/add (Anadiendo producto id {product_id} al carrito)")
        add_data = {
            "productId": product_id,
            "quantity": 2
        }
        status, body = make_request("/api/cart/add", method="POST", data=add_data, token=token)
        assert status == 200, f"Error: {status} - {body}"
        print(f"   [OK] {body.get('message')}")
        
        # 6. Test Obtener Carrito
        print("\n6. Probando GET /api/cart (Obtener carrito del usuario)")
        status, body = make_request("/api/cart", token=token)
        assert status == 200, f"Error: {status} - {body}"
        cart_items = body.get("cart", [])
        total = body.get("total", 0)
        print(f"   [OK] Carrito obtenido. Elementos: {len(cart_items)}, Total: {total} euros.")
        assert len(cart_items) > 0, "Error: El carrito deberia contener elementos"
        
        # 7. Test GraphQL para listar usuarios (Debe fallar para usuario normal - 403)
        print("\n7. Probando Mutation/Query de GraphQL (Listar usuarios - Debe denegar a usuario normal)")
        gql_query = {
            "query": "query { users { id username role } }"
        }
        status, body = make_request("/graphql", method="POST", data=gql_query, token=token)
        # Como es una peticion GraphQL, maneja la restriccion devolviendo errores en el cuerpo o HTTP 403.
        # En graphql.py pusimos _require_admin(current_user) que lanza HTTPException 403.
        assert status == 403 or (isinstance(body, dict) and "errors" in body), f"Se esperaba error de autorizacion, se obtuvo: {status} - {body}"
        print(f"   [OK] Autorizacion denegada correctamente para usuario normal: {status} - {body}")
        
    else:
        print("\n Omitiendo pruebas de carrito y GraphQL al no haber productos en base de datos.")
        
    print("\n Todas las pruebas automatizadas del API han pasado correctamente!")

if __name__ == "__main__":
    run_tests()
