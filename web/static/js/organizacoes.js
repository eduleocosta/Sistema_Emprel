document.addEventListener("DOMContentLoaded", function () {
    carregarOrganizacoes();

    document.getElementById("btn_salvar_org").addEventListener("click", function () {
        salvarOrganizacao();
    });
});

function carregarOrganizacoes() {
    fetch("/api/organizacoes")
        .then(function (r) { return r.json(); })
        .then(function (data) {
            var tbody = document.getElementById("tbody_org");
            tbody.innerHTML = "";
            data.forEach(function (item) {
                var tr = document.createElement("tr");
                tr.innerHTML =
                    "<td>" + escapeHtml(item.id) + "</td>" +
                    "<td>" + escapeHtml(item.nome || "") + "</td>" +
                    "<td>" + escapeHtml(item.descricao || "") + "</td>" +
                    "<td><button class='btn btn-sm btn-danger btn-excluir-org' data-id='" + item.id + "'>Excluir</button></td>";
                tbody.appendChild(tr);
            });

            tbody.querySelectorAll(".btn-excluir-org").forEach(function (btn) {
                btn.addEventListener("click", function () {
                    excluirOrganizacao(this.getAttribute("data-id"));
                });
            });
        });
}

function salvarOrganizacao() {
    var nome = document.getElementById("nova_org_nome").value.trim();
    var desc = document.getElementById("nova_org_desc").value.trim();

    if (!nome) {
        alert("Preencha o nome da organização");
        return;
    }

    var dados = {
        nome: nome,
        descricao: desc,
    };

    fetch("/api/organizacoes", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(dados),
    })
        .then(function (r) { return r.json(); })
        .then(function (result) {
            alert("Organização salva com sucesso!");
            carregarOrganizacoes();
            document.getElementById("nova_org_nome").value = "";
            document.getElementById("nova_org_desc").value = "";
        })
        .catch(function (err) {
            alert("Erro ao salvar: " + err.message);
        });
}

function excluirOrganizacao(id) {
    if (!confirm("Tem certeza que deseja excluir esta organização?")) return;
    fetch("/api/organizacoes/" + id, { method: "DELETE" })
        .then(function () {
            alert("Organização excluída com sucesso!");
            carregarOrganizacoes();
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