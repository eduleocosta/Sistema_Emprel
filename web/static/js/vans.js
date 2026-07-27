document.addEventListener("DOMContentLoaded", function () {
    carregarVans();

    document.getElementById("btn_salvar_van").addEventListener("click", function () {
        salvarVan();
    });
});

function carregarVans() {
    fetch("/api/vans")
        .then(function (r) { return r.json(); })
        .then(function (data) {
            var tbody = document.getElementById("tbody_vans");
            tbody.innerHTML = "";
            data.forEach(function (item) {
                var tr = document.createElement("tr");
                var ativa = item.ativa ? "Sim" : "Não";
                tr.innerHTML =
                    "<td>" + escapeHtml(item.id) + "</td>" +
                    "<td>" + escapeHtml(item.nome || "") + "</td>" +
                    "<td>" + escapeHtml(item.descricao || "") + "</td>" +
                    "<td>" + ativa + "</td>" +
                    "<td><button class='btn btn-sm btn-danger btn-excluir-van' data-id='" + item.id + "'>Excluir</button></td>";
                tbody.appendChild(tr);
            });

            tbody.querySelectorAll(".btn-excluir-van").forEach(function (btn) {
                btn.addEventListener("click", function () {
                    excluirVan(this.getAttribute("data-id"));
                });
            });
        });
}

function salvarVan() {
    var nome = document.getElementById("nova_van_nome").value.trim();
    var desc = document.getElementById("nova_van_desc").value.trim();

    if (!nome) {
        alert("Preencha o nome da van");
        return;
    }

    var dados = {
        nome: nome,
        descricao: desc,
        ativa: true,
    };

    fetch("/api/vans", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(dados),
    })
        .then(function (r) { return r.json(); })
        .then(function (result) {
            alert("Van salva com sucesso!");
            carregarVans();
            document.getElementById("nova_van_nome").value = "";
            document.getElementById("nova_van_desc").value = "";
        })
        .catch(function (err) {
            alert("Erro ao salvar: " + err.message);
        });
}

function excluirVan(id) {
    if (!confirm("Tem certeza que deseja excluir esta van?")) return;
    fetch("/api/vans/" + id, { method: "DELETE" })
        .then(function () {
            alert("Van excluída com sucesso!");
            carregarVans();
        })
        .catch(function (err) {
            alert("Erro ao excluir: " + err.message);
        });
}

function escapeHtml(text) {
    if (!text) return "";
    var div = document.createElement("div");
    div.appendChild(document.createTextNode(text));
    return div.innerHTML;
}