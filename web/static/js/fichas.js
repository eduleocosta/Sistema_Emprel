document.addEventListener("DOMContentLoaded", function () {
    carregarFichas();

    document.getElementById("btn_gerar_ficha").addEventListener("click", function () {
        gerarFicha();
    });
});

function carregarFichas() {
    fetch("/api/cadastros")
        .then(function (r) { return r.json(); })
        .then(function (data) {
            var tbody = document.getElementById("tbody_fichas");
            tbody.innerHTML = "";
            data.forEach(function (item) {
                var tr = document.createElement("tr");
                tr.innerHTML =
                    "<td>" + escapeHtml(item.protocolo || "") + "</td>" +
                    "<td>" + escapeHtml(item.nome || "") + "</td>" +
                    "<td>" + escapeHtml(item.cpf || "") + "</td>" +
                    "<td>" + escapeHtml(item.data || "") + "</td>" +
                    "<td>" + escapeHtml(item.acao || "") + "</td>" +
                    "<td>" + escapeHtml(item.servico || "") + "</td>";
                tbody.appendChild(tr);
            });
        });
}

function gerarFicha() {
    var protocolo = document.getElementById("ficha_protocolo").value.trim();

    if (!protocolo) {
        alert("Preencha o protocolo");
        return;
    }

    fetch("/api/cadastros")
        .then(function (r) { return r.json(); })
        .then(function (data) {
            var item = data.find(function (c) { return c.protocolo === protocolo; });
            if (!item) {
                alert("Cadastro não encontrado");
                return;
            }

            var preview = document.getElementById("ficha_preview");
            preview.innerHTML =
                "<div class='card'>" +
                "<div class='card-header bg-white'><strong>Ficha de Cadastro</strong></div>" +
                "<div class='card-body'>" +
                "<p><strong>Protocolo:</strong> " + escapeHtml(item.protocolo || "") + "</p>" +
                "<p><strong>CPF:</strong> " + escapeHtml(item.cpf || "") + "</p>" +
                "<p><strong>Nome:</strong> " + escapeHtml(item.nome || "") + "</p>" +
                "<p><strong>Telefone:</strong> " + escapeHtml(item.telefone || "") + "</p>" +
                "<p><strong>Data:</strong> " + escapeHtml(item.data || "") + "</p>" +
                "<p><strong>Ação:</strong> " + escapeHtml(item.acao || "") + "</p>" +
                "<p><strong>Serviço:</strong> " + escapeHtml(item.servico || "") + "</p>" +
                "</div></div>";
        });
}

function escapeHtml(text) {
    if (!text) return "";
    var div = document.createElement("div");
    div.appendChild(document.createTextNode(text));
    return div.innerHTML;
}