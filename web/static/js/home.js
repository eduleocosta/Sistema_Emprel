(function () {
    var acaoApi = "/api/acao-ativa";
    var sessionApi = "/api/session";

    function carregarAcaoAtiva() {
        fetch(acaoApi, { credentials: "same-origin" })
            .then(function (r) {
                if (r.status === 401 || r.status === 302) {
                    window.location.href = "/login";
                    return Promise.reject("Não autenticado");
                }
                return r.json().catch(function () {
                    return {};
                });
            })
            .then(function (acao) {
                atualizarBlocoAcaoAtiva(acao);
                atualizarBotaoCadastro(acao);
            })
            .catch(function () {
                atualizarBlocoAcaoAtiva({});
                atualizarBotaoCadastro({});
            });
    }

    function atualizarBlocoAcaoAtiva(acao) {
        var el = document.getElementById("acao_ativa_texto");
        var bloco = document.getElementById("bloco_acao_ativa");
        if (!el || !bloco) {
            return;
        }
        if (!acao || !acao.data || !acao.local) {
            el.textContent = "Ação ativa: Nenhuma ação selecionada   |   Serviço: Nenhum serviço selecionado";
            bloco.classList.remove("alert-success");
            bloco.classList.add("alert-warning");
            return;
        }
        el.textContent = "Ação ativa: " + (acao.data || "") + " - " + (acao.local || "");
        bloco.classList.remove("alert-warning");
        bloco.classList.add("alert-success");
    }

    function atualizarBotaoCadastro(acao) {
        var btn = document.getElementById("btn_cadastro_home");
        if (!btn) {
            return;
        }
        if (acao && acao.data && acao.local) {
            btn.textContent = "Ação Ativa";
            btn.className = btn.className.replace("btn-primary", "btn-success");
        } else {
            btn.textContent = "Cadastro";
            btn.className = btn.className.replace("btn-success", "btn-primary");
        }
    }

    function ajustarBotoesPorPerfil() {
        fetch(sessionApi, { credentials: "same-origin" })
            .then(function (r) { return r.json(); })
            .then(function (data) {
                var usuario = data.user || {};
                var vanHome = document.getElementById("btn_van_home");
                var acessoHome = document.getElementById("btn_acesso_home");
                if (vanHome) {
                    vanHome.style.display = usuario.perfil === "admin" ? "" : "none";
                }
                if (acessoHome) {
                    acessoHome.style.display = usuario.perfil === "admin" ? "" : "none";
                }
            })
            .catch(function () {
                window.location.href = "/login";
            });
    }

    carregarAcaoAtiva();
    ajustarBotoesPorPerfil();
})();
