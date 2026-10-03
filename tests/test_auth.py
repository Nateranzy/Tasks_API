CADASTRO = {"email": "a@gmail.com", "senha": "senha12345"}


def test_cadastro_ok(client):
    resp = client.post("/auth/register", json=CADASTRO)
    assert resp.status_code == 201
    corpo = resp.json()
    assert corpo["email"] == "a@gmail.com"
    assert "senha" not in corpo
    assert "senha_hash" not in corpo


def test_cadastro_email_repetido(client):
    client.post("/auth/register", json=CADASTRO)
    resp = client.post("/auth/register", json=CADASTRO)
    assert resp.status_code == 409


def test_cadastro_ignora_maiusculas_no_email(client):
    client.post(
        "/auth/register", json={"email": "Nate@gmail.com", "senha": "senha12345"}
    )
    resp = client.post(
        "/auth/register", json={"email": "nate@gmail.com", "senha": "senha12345"}
    )
    assert resp.status_code == 409


def test_cadastro_senha_curta(client):
    resp = client.post(
        "/auth/register", json={"email": "a@gmail.com", "senha": "123"}
    )
    assert resp.status_code == 422


def test_cadastro_email_invalido(client):
    resp = client.post(
        "/auth/register", json={"email": "abc", "senha": "senha12345"}
    )
    assert resp.status_code == 422


def test_login_ok(client):
    client.post("/auth/register", json=CADASTRO)
    resp = client.post(
        "/auth/login", data={"username": "a@gmail.com", "password": "senha12345"}
    )
    assert resp.status_code == 200
    assert resp.json()["token_type"] == "bearer"
    assert resp.json()["access_token"]


def test_login_senha_errada(client):
    client.post("/auth/register", json=CADASTRO)
    resp = client.post(
        "/auth/login", data={"username": "a@gmail.com", "password": "errada123"}
    )
    assert resp.status_code == 401


def test_login_nao_revela_se_o_email_existe(client):
    client.post("/auth/register", json=CADASTRO)
    senha_errada = client.post(
        "/auth/login", data={"username": "a@gmail.com", "password": "errada123"}
    )
    email_inexistente = client.post(
        "/auth/login", data={"username": "nao@gmail.com", "password": "qualquer123"}
    )
    assert senha_errada.status_code == 401
    assert email_inexistente.status_code == 401
    assert senha_errada.json() == email_inexistente.json()