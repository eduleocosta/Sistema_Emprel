document.addEventListener("DOMContentLoaded", function () {
    carregarEntregas();

    document.getElementById("btn_salvar_entrega").addEventListener("click", function () {
        salvarEntrega();
    });
});

function carregarEntregas() {
    fetch("/api/entregas")
        .then(function (r) { return r.json(); })
        .then(function (data) {
            var tbody = document.getElementById("tbody_entregas");
            tbody.innerHTML = "";
            data.forEach(function (item) {
                var tr = document.createElement("tr");
                tr.innerHTML =
                    "<td>" + escapeHtml(item.protocolo || "") + "</td>" +
                    "<td>" + escapeHtml(item.nome || "") + "</td>" +
                    "<td>" + escapeHtml(item.cpf || "") + "</td>" +
                    "<td>" + escapeHtml(item.telefone || "") + "</td>" +
                    "<td>" + escapeHtml(item.data_acao || "") + "</td>" +
                    "<td>" + escapeHtml(item.acao || "") + "</td>" +
                    "<td>" + escapeHtml(item.operador || "") + "</td>" +
                    "<td>" + escapeHtml(item.data_entrega || "") + "</td>";
                tbody.appendChild(tr);
            });
        });
}

function salvarEntrega() {
    var protocolo = document.getElementById("ent_entrega_protocolo").value.trim();
    var nome = document.getElementById("ent_entrega_nome").value.trim();
    var cpf = document.getElementById("ent_entrega_cpf").value.trim();
    var telefone = document.getElementById("ent_entrega_telefone").value.trim();
    var data = document.getElementById("ent_entrega_data").value.trim();
    var acao = document.getElementById("ent_entrega_acao").value.trim();
    var operador = document.getElementById("ent_entrega_operador").value.trim();

    if (!protocolo || !nome) {
        alert("Preencha pelo menos o Protocolo e o Nome");
        return;
    }

    var dados = {
        protocolo: protocolo,
        nome: nome,
        cpf: cpf,
        telefone: telefone,
        data_acao: data,
        acao: acao,
        operador: operador,
        data_entrega: new Date().toLocaleString("pt-BR"),
    };

    fetch("/api/entregas", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(dados),
    })
        .then(function (r) { return r.json(); })
        .then(function (result) {
            alert("Entrega registrada com sucesso!");
            carregarEntregas();
            limparCampos();
        })
        .catch(function (err) {
            alert("Erro ao salvar: " + err.message);
        });
}

function limparCampos() {
    document.getElementById("ent_entrega_protocolo").value = "";
    document.getElementById("ent_entrega_nome").value = "";
    document.getElementById("ent_entrega_cpf").value = "";
    document.getElementById("ent_entrega_telefone").value = "";
    document.getElementById("ent_entrega_data").value = "";
    document.getElementById("ent_entrega_acao").value = "";
    document.getElementById("ent_entrega_operador").value = "";
}

function escapeHtml(text) {
    if (!text) return "";
    var div = document.createElement("div");
    div.appendChild(document.createTextNode(text));
    return div.innerHTML;
}