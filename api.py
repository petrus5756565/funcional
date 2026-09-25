"""API mínima para autenticação do app de tarefas."""
from flask import Flask, jsonify, request

app = Flask(__name__)

EMAIL_TESTE = "admin@gmail.com"
SENHA_TESTE = "1234"


@app.post("/api/login")
def login():
    dados = request.get_json(silent=True) or {}
    email = (dados.get("email") or "").strip().lower()
    senha = (dados.get("senha") or "").strip()

    if email == EMAIL_TESTE and senha == SENHA_TESTE:
        return jsonify({"ok": True, "message": "Login realizado com sucesso."}), 200

    return jsonify({"ok": False, "message": "E-mail ou senha incorretos."}), 401


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
