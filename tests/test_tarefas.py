def test_rotas_exigem_login(client):
    assert client.get("/tarefas").status_code == 401
    assert client.post("/tarefas", json={"titulo": "x"}).status_code == 401


def test_token_falso_e_recusado(client):
    resp = client.get("/tarefas", headers={"Authorization": "Bearer token-falso"})
    assert resp.status_code == 401


def test_criar_e_listar(client, login):
    h = login()
    resp = client.post(
        "/tarefas",
        json={"titulo": "Estudar", "descricao": "pytest"},
        headers=h,
    )
    assert resp.status_code == 201
    assert resp.json()["concluida"] is False

    lista = client.get("/tarefas", headers=h).json()
    assert len(lista) == 1
    assert lista[0]["titulo"] == "Estudar"


def test_titulo_vazio_e_rejeitado(client, login):
    h = login()
    resp = client.post("/tarefas", json={"titulo": ""}, headers=h)
    assert resp.status_code == 422


def test_marcar_como_concluida(client, login):
    h = login()
    tarefa = client.post("/tarefas", json={"titulo": "x"}, headers=h).json()
    resp = client.patch(
        f"/tarefas/{tarefa['id']}", json={"concluida": True}, headers=h
    )
    assert resp.status_code == 200
    assert resp.json()["concluida"] is True
    assert resp.json()["titulo"] == "x"


def test_filtrar_por_concluida(client, login):
    h = login()
    t1 = client.post("/tarefas", json={"titulo": "a"}, headers=h).json()
    client.post("/tarefas", json={"titulo": "b"}, headers=h)
    client.patch(f"/tarefas/{t1['id']}", json={"concluida": True}, headers=h)

    feitas = client.get("/tarefas?concluida=true", headers=h).json()
    pendentes = client.get("/tarefas?concluida=false", headers=h).json()
    assert [t["titulo"] for t in feitas] == ["a"]
    assert [t["titulo"] for t in pendentes] == ["b"]


def test_apagar_tarefa(client, login):
    h = login()
    tarefa = client.post("/tarefas", json={"titulo": "x"}, headers=h).json()
    resp = client.delete(f"/tarefas/{tarefa['id']}", headers=h)
    assert resp.status_code == 204
    assert client.get(f"/tarefas/{tarefa['id']}", headers=h).status_code == 404


def test_tarefa_inexistente(client, login):
    h = login()
    assert client.get("/tarefas/999", headers=h).status_code == 404


def test_isolamento_entre_usuarios(client, login):
    h_a = login("a@gmail.com")
    h_b = login("b@gmail.com")
    tarefa = client.post("/tarefas", json={"titulo": "privada"}, headers=h_a).json()
    tid = tarefa["id"]

    # O usuário B não vê, não lê, não altera e não apaga a tarefa do A
    assert client.get("/tarefas", headers=h_b).json() == []
    assert client.get(f"/tarefas/{tid}", headers=h_b).status_code == 404
    assert (
        client.patch(
            f"/tarefas/{tid}", json={"titulo": "invadida"}, headers=h_b
        ).status_code
        == 404
    )
    assert client.delete(f"/tarefas/{tid}", headers=h_b).status_code == 404

    # E a tarefa continua intacta para o dono
    dono = client.get(f"/tarefas/{tid}", headers=h_a)
    assert dono.status_code == 200
    assert dono.json()["titulo"] == "privada"