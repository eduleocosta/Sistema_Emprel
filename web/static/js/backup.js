document.addEventListener("DOMContentLoaded", function () {
    carregarBackups();

    document.getElementById("btn_fazer_backup").addEventListener("click", function () {
        fazerBackup();
    });
});

function carregarBackups() {
    fetch("/api/backup")
        .then(function (r) { return r.json(); })
        .then(function (data) {
            var lista = document.getElementById("lista_backups");
            lista.innerHTML = "";
            if (data.file) {
                lista.innerHTML = "<p>Backup mais recente: " + escapeHtml(data.file) + "</p>";
            } else {
                lista.innerHTML = "<p class='text-muted'>Nenhum backup encontrado.</p>";
            }
        });
}

function fazerBackup() {
    fetch("/api/backup", { method: "POST" })
        .then(function (r) { return r.json(); })
        .then(function (result) {
            if (result.status === "ok") {
                alert("Backup realizado com sucesso!");
                carregarBackups();
            } else {
                alert("Erro ao fazer backup");
            }
        })
        .catch(function (err) {
            alert("Erro: " + err.message);
        });
}

function escapeHtml(text) {
    if (!text) return "";
    var div = document.createElement("div");
    div.appendChild(document.createTextNode(text));
    return div.innerHTML;
}