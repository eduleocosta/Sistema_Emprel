document.addEventListener("DOMContentLoaded", function () {
    carregarEstatisticas();
    carregarCadastrosPorAcao();

    document.getElementById("btn_rel_periodo").addEventListener("click", function () {
        carregarCadastrosPorPeriodo();
    });
});

function carregarEstatisticas() {
    fetch("/api/relatorios/estatisticas")
        .then(function (r) { return r.json(); })
        .then(function (data) {
            document.getElementById("stat_total").textContent = data.total_cadastros;
            document.getElementById("stat_acoes").textContent = data.total_acoes;
            document.getElementById("stat_vans").textContent = data.total_vans;
        });
}

function carregarCadastrosPorAcao() {
    fetch("/api/relatorios/cadastros-por-acao")
        .then(function (r) { return r.json(); })
        .then(function (data) {
            var tbody = document.getElementById("tbody_acoes");
            tbody.innerHTML = "";
            data.forEach(function (item) {
                var tr = document.createElement("tr");
                tr.innerHTML =
                    "<td>" + escapeHtml(item.acao_nome) + "</td>" +
                    "<td>" + item.total + "</td>";
                tbody.appendChild(tr);
            });
        });
}

function carregarCadastrosPorPeriodo() {
    var de = document.getElementById("rel_de").value.trim();
    var ate = document.getElementById("rel_ate").value.trim();
    var url = "/api/relatorios/cadastros-por-periodo";
    if (de && ate) {
        url += "?de=" + encodeURIComponent(de) + "&ate=" + encodeURIComponent(ate);
    }
    fetch(url)
        .then(function (r) { return r.json(); })
        .then(function (data) {
            var tbody = document.getElementById("tbody_periodo");
            tbody.innerHTML = "";
            data.forEach(function (item) {
                var tr = document.createElement("tr");
                tr.innerHTML =
                    "<td>" + escapeHtml(item.protocolo || "") + "</td>" +
                    "<td>" + escapeHtml(item.nome || "") + "</td>" +
                    "<td>" + escapeHtml(item.cpf || "") + "</td>" +
                    "<td>" + escapeHtml(item.telefone || "") + "</td>" +
                    "<td>" + escapeHtml(item.data || "") + "</td>" +
                    "<td>" + escapeHtml(item.acao || "") + "</td>" +
                    "<td>" + escapeHtml(item.servico || "") + "</td>";
                tbody.appendChild(tr);
            });
        });
}

function escapeHtml(text) {
    if (!text) return "";
    var div = document.createElement("div");
    div.appendChild(document.createTextNode(text));
    return div.innerHTML;
}