def payload(**kwargs):
    data = {"title":"Мастер и Маргарита","author":"М. Булгаков","genre":"Роман",
            "status":"В планах","added_on":"2026-11-24","rating":5,"notes":"Для обсуждения"}
    data.update(kwargs)
    return data

def test_create_and_list_book(client):
    r=client.post("/api/books",json=payload())
    assert r.status_code==201
    assert r.json()["title"]=="Мастер и Маргарита"
    assert len(client.get("/api/books").json())==1

def test_update_book(client):
    book=client.post("/api/books",json=payload()).json()
    changed=client.put(f"/api/books/{book['id']}",json=payload(status="Прочитана",rating=4))
    assert changed.status_code==200
    assert changed.json()["status"]=="Прочитана"
    assert changed.json()["rating"]==4

def test_delete_book(client):
    book=client.post("/api/books",json=payload()).json()
    assert client.delete(f"/api/books/{book['id']}").status_code==204
    assert client.get("/api/books").json()==[]

def test_search_by_author(client):
    client.post("/api/books",json=payload())
    client.post("/api/books",json=payload(title="1984",author="Джордж Оруэлл"))
    result=client.get("/api/books",params={"search":"Оруэлл"})
    assert len(result.json())==1 and result.json()[0]["title"]=="1984"

def test_filter_by_status(client):
    client.post("/api/books",json=payload(status="Читаю"))
    client.post("/api/books",json=payload(title="1984",author="Оруэлл",status="В планах"))
    result=client.get("/api/books",params={"status":"Читаю"})
    assert len(result.json())==1 and result.json()[0]["status"]=="Читаю"

def test_validation_rating_and_required_fields(client):
    assert client.post("/api/books",json=payload(rating=8)).status_code==422
    assert client.post("/api/books",json=payload(title="   ")).status_code==422

def test_not_found(client):
    assert client.put("/api/books/999",json=payload()).status_code==404
    assert client.delete("/api/books/999").status_code==404

def test_statistics(client):
    client.post("/api/books",json=payload(status="Прочитана",rating=4))
    client.post("/api/books",json=payload(title="1984",author="Оруэлл",status="Читаю",rating=2))
    stats=client.get("/api/statistics").json()
    assert stats["total"]==2 and stats["read"]==1 and stats["reading"]==1
    assert stats["average_rating"]==3.0
