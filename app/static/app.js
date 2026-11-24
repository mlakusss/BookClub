const $ = id => document.getElementById(id);
const today = new Date().toISOString().slice(0,10);
$("added_on").value = today;
function log(message){const li=document.createElement("li");li.textContent=`${new Date().toLocaleTimeString("ru-RU")} — ${message}`;$("log").prepend(li);}
async function request(url, options={}){const r=await fetch(url,{headers:{"Content-Type":"application/json"},...options});if(!r.ok){let d={};try{d=await r.json()}catch{}throw new Error(d.detail||`Ошибка ${r.status}`)}return r.status===204?null:r.json()}
function esc(s){return String(s??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]))}
async function load(){
 try{
  const q=new URLSearchParams({search:$("search").value,status:$("filterStatus").value});
  const [books,stats]=await Promise.all([request(`/api/books?${q}`),request("/api/statistics")]);
  $("total").textContent=stats.total;$("read").textContent=stats.read;$("reading").textContent=stats.reading;$("planned").textContent=stats.planned;$("rating").textContent=stats.average_rating??"—";
  $("count").textContent=`${books.length} записей`;$("empty").classList.toggle("hidden",books.length!==0);
  $("bookRows").innerHTML=books.map(b=>`<tr><td><strong>${esc(b.title)}</strong><small>${esc(b.author)} · ${b.added_on}</small></td><td>${esc(b.genre)}</td><td><span class="status ${b.status==="Прочитана"?"s-read":b.status==="Читаю"?"s-reading":"s-planned"}">${esc(b.status)}</span></td><td>${b.rating?`★ ${b.rating}/5`:"—"}</td><td><button class="mini" onclick="editBook(${b.id})">Изменить</button><button class="mini danger" onclick="deleteBook(${b.id})">Удалить</button></td></tr>`).join("");
  const values=[["Прочитано",stats.read],["Читают",stats.reading],["В планах",stats.planned]],max=Math.max(1,...values.map(v=>v[1]));
  $("bars").innerHTML=values.map(([n,v])=>`<div class="bar-row"><span>${n}</span><div class="track"><div class="fill" style="width:${v/max*100}%"></div></div><b>${v}</b></div>`).join("");
 }catch(e){log(`Ошибка загрузки: ${e.message}`)}
}
$("bookForm").addEventListener("submit",async e=>{
 e.preventDefault();const id=$("bookId").value;
 const data={title:$("title").value,author:$("author").value,genre:$("genre").value||"Не указан",status:$("status").value,added_on:$("added_on").value,rating:$("rating").value?Number($("rating").value):null,notes:$("notes").value};
 try{await request(id?`/api/books/${id}`:"/api/books",{method:id?"PUT":"POST",body:JSON.stringify(data)});log(id?"Книга обновлена":"Добавлена новая книга");resetForm();await load()}catch(err){alert(err.message);log(`Ошибка сохранения: ${err.message}`)}
});
window.editBook=async id=>{try{const b=(await request("/api/books")).find(x=>x.id===id);if(!b)return;$("bookId").value=b.id;$("title").value=b.title;$("author").value=b.author;$("genre").value=b.genre;$("status").value=b.status;$("added_on").value=b.added_on;$("rating").value=b.rating??"";$("notes").value=b.notes;$("formTitle").textContent="Редактировать книгу";$("submitBtn").textContent="Сохранить изменения";$("cancel").classList.remove("hidden");window.scrollTo({top:0,behavior:"smooth"})}catch(e){alert(e.message)}};
window.deleteBook=async id=>{if(!confirm("Удалить книгу из каталога?"))return;try{await request(`/api/books/${id}`,{method:"DELETE"});log(`Книга ID ${id} удалена`);await load()}catch(e){alert(e.message)}};
function resetForm(){$("bookForm").reset();$("bookId").value="";$("added_on").value=today;$("formTitle").textContent="Добавить книгу";$("submitBtn").textContent="Сохранить книгу";$("cancel").classList.add("hidden")}
$("cancel").onclick=resetForm;$("refresh").onclick=()=>{load();log("Каталог обновлен")};$("clearLog").onclick=()=>$("log").replaceChildren();$("search").oninput=load;$("filterStatus").onchange=load;load();
