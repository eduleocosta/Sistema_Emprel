document.addEventListener("DOMContentLoaded", function () {
    carregarServicos();

    document.getElementById("btn_salvar_servico").addEventListener("click", function () {
        salvarServico();
    });
});

function carregarServicos() {
    fetch("/api/servicos")
        .then(function (r) { return r.json(); })
        .then(function (data) {
            var tbody = document.getElementById("tbody_servicos");
            tbody.innerHTML = "";
            data.forEach(function (item) {
                var tr = document.createElement("tr");
                tr.innerHTML =
                    "<td>" + escapeHtml(item.id) + "</td>" +
                    "<td>" + escapeHtml(item.nome || "") + "</td>" +
                    "<td>" + escapeHtml(item.descricao || "") + "</td>" +
                    "<td><button class='btn btn-sm btn-danger btn-excluir-servico' data-id='" + item.id + "'>Excluir</button></td>";
                tbody.appendChild(tr);
            });

            tbody.querySelectorAll(".btn-excluir-servico").forEach(function (btn) {
                btn.addEventListener("click", function () {
                    excluirServico(this.getAttribute("data-id"));
                });
            });
        });
}

function salvarServico() {
    var nome = document.getElementById("novo_servico_nome").value.trim();
    var desc = document.getElementById("novo_servico_desc").value.trim();

    if (!nome) {
        alert("Preencha o nome do serviço");
        return;
    }

    var dados = {
        nome: nome,
        descricao: desc,
    };

    fetch("/api/servicos", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(dados),
    })
        .then(function (r) { return r.json(); })
        .then(function (result) {
            alert("Serviço salvo com sucesso!");
            carregarServicos();
            document.getElementById("novo_servico_nome").value = "";
            document.getElementById("novo_servico_desc").value = "";
        })
        .catch(function (err) {
            alert("Erro ao salvar: " + err.message);
        });
}

function excluirServico(id) {
    if (!confirm("Tem certeza que deseja excluir este serviço?")) return;
    fetch("/api/servicos/" + id, { method: "DELETE" })
        .then(function () {
            alert("Serviço excluído com sucesso!");
            carregarServicos();
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