document.addEventListener("DOMContentLoaded", function () {
    carregarAcoes();

    document.getElementById("btn_salvar_acao").addEventListener("click", function () {
        salvarAcao();
    });
});

function carregarAcoes() {
    fetch("/api/acoes", { credentials: "same-origin" })
        .then(function (r) {
            if (r.status === 401 || r.status === 302) {
                window.location.href = "/login";
                return Promise.reject("Não autenticado");
            }
            return r.json().catch(function () {
                return [];
            });
        })
        .then(function (data) {
            var tbody = document.getElementById("tbody_acoes");
            if (!tbody) {
                return;
            }
            tbody.innerHTML = "";
            data.forEach(function (item) {
                var tr = document.createElement("tr");
                var status = item.finalizada ? "Finalizada" : "Ativa";
                var statusClass = item.finalizada ? "bg-secondary" : "bg-success";
                tr.innerHTML =
                    "<td>" + escapeHtml(item.id) + "</td>" +
                    "<td>" + escapeHtml(item.nome || "") + "</td>" +
                    "<td>" + escapeHtml(item.local || "") + "</td>" +
                    "<td>" + escapeHtml(item.data || "") + "</td>" +
                    "<td><span class='badge " + statusClass + "'>" + status + "</span></td>" +
                    "<td><button class='btn btn-sm btn-danger btn-excluir-acao' data-id='" + item.id + "'>Excluir</button></td>";
                tbody.appendChild(tr);
            });

            tbody.querySelectorAll(".btn-excluir-acao").forEach(function (btn) {
                btn.addEventListener("click", function () {
                    excluirAcao(this.getAttribute("data-id"));
                });
            });
        })
        .catch(function (err) {
            if (err && err.message && err.message !== "Não autenticado") {
                alert("Erro ao carregar ações: " + err.message);
            }
        });
}

function salvarAcao() {
    var nome = document.getElementById("nova_acao_nome").value.trim();
    var local = document.getElementById("nova_acao_local").value.trim();
    var data = document.getElementById("nova_acao_data").value.trim();

    if (!nome) {
        alert("Preencha o nome da ação");
        return;
    }

    var dados = {
        nome: nome,
        local: local,
        data: data,
    };

    fetch("/api/acoes", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(dados),
    })
        .then(function (r) { return r.json(); })
        .then(function (result) {
            alert("Ação salva com sucesso!");
            carregarAcoes();
            document.getElementById("nova_acao_nome").value = "";
            document.getElementById("nova_acao_local").value = "";
            document.getElementById("nova_acao_data").value = "";
        })
        .catch(function (err) {
            alert("Erro ao salvar: " + err.message);
        });
}

function excluirAcao(id) {
    if (!confirm("Tem certeza que deseja excluir esta ação?")) return;
    var url = "/api/acoes/" + id;
    console.log("[acoes] DELETE", url);
    fetch(url, {
        method: "DELETE",
        credentials: "same-origin",
    })
        .then(function (r) {
            console.log("[acoes] DELETE status", r.status, "location", r.headers.get("location"));
            return r.text().then(function (txt) {
                console.log("[acoes] DELETE body", txt);
                return { status: r.status, text: txt };
            });
        })
        .then(function (res) {
            if (res.status === 404) {
                console.log("[acoes] DELETE 404 for", id);
                alert("Ação não encontrada no backend. Atualizando a lista...");
                carregarAcoes();
                return;
            }
            if (res.status === 401 || res.status === 302) {
                alert("Sessão expirada. Voltando para o login.");
                window.location.href = "/login";
                return;
            }
            try {
                var json = JSON.parse(res.text || "{}");
                if (json.status !== "ok") {
                    alert("Erro ao excluir: " + (json.message || res.text || "status=" + res.status));
                    return;
                }
            } catch (e) {
                alert("Erro ao excluir: resposta inesperada.");
                return;
            }
            alert("Ação excluída com sucesso!");
            carregarAcoes();
        })
        .catch(function (err) {
            console.log("[acoes] DELETE error", err);
            alert("Erro ao excluir: " + err.message);
        });
}

function escapeHtml(text) {
    if (!text) return "";
    var div = document.createElement("div");
    div.appendChild(document.createTextNode(text));
    return div.innerHTML;
}