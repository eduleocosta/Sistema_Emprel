(function () {
    var modalUsuario = null;
    var modalSenha = null;
    var usuarioEditando = null;
    var meuCpf = "";

    function somente_digits(value) {
        return (value || "").replace(/\D/g, "");
    }

    function aplicarMascaraCPF(value) {
        var digits = somente_digits(value).slice(0, 11);
        var formatted = "";
        if (digits.length > 0) {
            formatted += digits.slice(0, 3);
        }
        if (digits.length >= 4) {
            formatted += "." + digits.slice(3, 6);
        }
        if (digits.length >= 7) {
            formatted += "." + digits.slice(6, 9);
        }
        if (digits.length >= 10) {
            formatted += "-" + digits.slice(9, 11);
        }
        return formatted;
    }

    function limparFormularioUsuario() {
        document.getElementById("form_usuario").reset();
        document.getElementById("usuario_cpf").value = "";
        document.getElementById("usuario_cpf_visual").value = "";
        document.getElementById("campo_senha_container").style.display = "";
    }

    function abrirModalCriar() {
        usuarioEditando = null;
        limparFormularioUsuario();
        document.getElementById("modal_usuario_titulo").textContent = "Novo Usuário";
        document.getElementById("campo_senha_container").style.display = "";
        document.getElementById("usuario_cpf_visual").readOnly = false;
        modalUsuario.show();
    }

    function abrirModalEdicao(usuario) {
        usuarioEditando = usuario;
        limparFormularioUsuario();
        document.getElementById("modal_usuario_titulo").textContent = "Editar Usuário";
        document.getElementById("usuario_cpf").value = usuario.cpf || "";
        document.getElementById("usuario_cpf_visual").value = usuario.cpf ? aplicarMascaraCPF(usuario.cpf) : "";
        document.getElementById("usuario_cpf_visual").readOnly = true;
        document.getElementById("usuario_nome").value = usuario.nome || "";
        document.getElementById("usuario_perfil").value = usuario.perfil || "user";
        document.getElementById("usuario_dn").value = usuario.data_nascimento || "";
        document.getElementById("usuario_email").value = usuario.email || "";
        document.getElementById("campo_senha_container").style.display = "none";
        modalUsuario.show();
    }

    function abrirModalSenha(cpf) {
        document.getElementById("form_senha").reset();
        document.getElementById("senha_cpf").value = cpf || "";
        modalSenha.show();
    }

    async function carregarUsuarios(termo) {
        var url = "/api/usuarios";
        if (termo) {
            url += "?pesquisa=" + encodeURIComponent(termo);
        }
        var response = await fetch(url, { credentials: "same-origin" });
        if (response.status === 401 || response.status === 302) {
            window.location.href = "/login";
            return;
        }
        var usuarios = await response.json().catch(function () { return []; });
        renderizarUsuarios(usuarios);
    }

    async function carregarSessao() {
        var response = await fetch("/api/session", { credentials: "same-origin" });
        var data = await response.json().catch(function () { return {}; });
        var usuario = data.user || {};
        var isAdmin = usuario.perfil === "admin";

        var cardLista = document.getElementById("card_lista_usuarios");
        var btnNovo = document.getElementById("btn_novo_usuario");
        var cardMeusDados = document.getElementById("card_meus_dados");

        if (cardLista) {
            cardLista.classList.toggle("d-none", !isAdmin);
        }
        if (btnNovo) {
            btnNovo.classList.toggle("d-none", !isAdmin);
        }
        if (cardMeusDados) {
            cardMeusDados.classList.toggle("d-none", isAdmin);
        }

        meuCpf = usuario.cpf || "";
        if (!isAdmin && meuCpf) {
            carregarMeusDados(meuCpf);
        }

        if (isAdmin) {
            carregarUsuarios();
        }
    }

    async function carregarMeusDados(cpf) {
        var response = await fetch("/api/usuarios", { credentials: "same-origin" });
        if (response.status === 401 || response.status === 302) {
            window.location.href = "/login";
            return;
        }
        var usuarios = await response.json().catch(function () { return []; });
        var usuario = usuarios.find(function (u) { return u.cpf === cpf; });
        if (!usuario) {
            return;
        }
        document.getElementById("meu_cpf").value = usuario.cpf ? aplicarMascaraCPF(usuario.cpf) : "";
        document.getElementById("meu_nome").value = usuario.nome || "";
        document.getElementById("meu_email").value = usuario.email || "";
        document.getElementById("meu_dn").value = usuario.data_nascimento || "";
    }

    function renderizarUsuarios(usuarios) {
        var tbody = document.getElementById("tbody_usuarios");
        if (!tbody) {
            return;
        }
        tbody.innerHTML = "";
        usuarios.forEach(function (u) {
            var tr = document.createElement("tr");
            var status = u.ativo !== false ? "Ativo" : "Inativo";
            var classeStatus = u.ativo !== false ? "text-success" : "text-danger";
            tr.innerHTML = "<td>" + (u.cpf || "") + "</td>" +
                "<td>" + (u.nome || "") + "</td>" +
                "<td>" + (u.perfil || "") + "</td>" +
                "<td>" + (u.email || "") + "</td>" +
                "<td class='" + classeStatus + "'>" + status + "</td>" +
                "<td>" +
                "<button class='btn btn-sm btn-primary btn-editar' data-cpf='" + (u.cpf || "") + "'>Editar</button> " +
                "<button class='btn btn-sm btn-warning btn-senha' data-cpf='" + (u.cpf || "") + "'>Senha</button> " +
                "<button class='btn btn-sm btn-success btn-status' data-cpf='" + (u.cpf || "") + "' data-ativo='" + (u.ativo !== false) + "'>" + (u.ativo !== false ? "Desativar" : "Ativar") + "</button> " +
                "<button class='btn btn-sm btn-danger btn-excluir' data-cpf='" + (u.cpf || "") + "'>Excluir</button>" +
                "</td>";
            tbody.appendChild(tr);
        });

        tbody.querySelectorAll(".btn-editar").forEach(function (btn) {
            btn.addEventListener("click", function () {
                var cpf = this.getAttribute("data-cpf");
                var usuario = usuarios.find(function (u) { return u.cpf === cpf; });
                if (usuario) {
                    abrirModalEdicao(usuario);
                }
            });
        });

        tbody.querySelectorAll(".btn-senha").forEach(function (btn) {
            btn.addEventListener("click", function () {
                abrirModalSenha(this.getAttribute("data-cpf"));
            });
        });

        tbody.querySelectorAll(".btn-status").forEach(function (btn) {
            btn.addEventListener("click", function () {
                var cpf = this.getAttribute("data-cpf");
                var ativo = this.getAttribute("data-ativo") === "true";
                alternarStatus(cpf, !ativo);
            });
        });

        tbody.querySelectorAll(".btn-excluir").forEach(function (btn) {
            btn.addEventListener("click", function () {
                var cpf = this.getAttribute("data-cpf");
                if (confirm("Deseja excluir o usuário " + cpf + "?")) {
                    excluirUsuario(cpf);
                }
            });
        });
    }

    async function salvarUsuario() {
        var cpfRaw = document.getElementById("usuario_cpf_visual").value;
        var cpf = somente_digits(cpfRaw);
        var nome = document.getElementById("usuario_nome").value.trim();
        var perfil = document.getElementById("usuario_perfil").value;
        var dn = document.getElementById("usuario_dn").value.trim();
        var email = document.getElementById("usuario_email").value.trim();
        var senha = document.getElementById("usuario_senha").value.trim();

        if (!cpf || cpf.length !== 11) {
            alert("CPF inválido.");
            return;
        }
        if (!nome) {
            alert("Informe o nome.");
            return;
        }

        var payload = {
            cpf: cpf,
            nome: nome,
            perfil: perfil,
            data_nascimento: dn,
            email: email,
            senha: senha || undefined,
        };

        var url = usuarioEditando ? "/api/usuarios/" + encodeURIComponent(usuarioEditando.cpf || "") : "/api/usuarios";
        var method = usuarioEditando ? "PUT" : "POST";

        var response = await fetch(url, {
            method: method,
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
            credentials: "same-origin",
        });
        var result = await response.json().catch(function () { return {}; });
        if (result.status === "ok") {
            alert(usuarioEditando ? "Usuário atualizado." : "Usuário criado.");
            modalUsuario.hide();
            carregarUsuarios();
        } else {
            alert(result.message || "Erro ao salvar.");
        }
    }

    async function salvarMeusDados() {
        var nome = document.getElementById("meu_nome").value.trim();
        var email = document.getElementById("meu_email").value.trim();
        var dn = document.getElementById("meu_dn").value.trim();
        if (!nome) {
            alert("Informe o nome.");
            return;
        }
        var response = await fetch("/api/usuarios/" + encodeURIComponent(meuCpf), {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ nome: nome, email: email, data_nascimento: dn }),
            credentials: "same-origin",
        });
        var result = await response.json().catch(function () { return {}; });
        if (result.status === "ok") {
            alert("Dados atualizados.");
        } else {
            alert(result.message || "Erro ao salvar.");
        }
    }

    async function redefinirSenha() {
        var cpf = document.getElementById("senha_cpf").value;
        var senha = document.getElementById("nova_senha").value.trim();
        var confirmar = document.getElementById("confirmar_senha").value.trim();
        if (!senha || senha.length < 4) {
            alert("Senha deve ter ao menos 4 caracteres.");
            return;
        }
        if (senha !== confirmar) {
            alert("Senhas não coincidem.");
            return;
        }
        var response = await fetch("/api/usuarios/" + encodeURIComponent(cpf) + "/senha", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ senha: senha }),
            credentials: "same-origin",
        });
        var result = await response.json().catch(function () { return {}; });
        if (result.status === "ok") {
            alert("Senha redefinida.");
            modalSenha.hide();
        } else {
            alert(result.message || "Erro ao redefinir senha.");
        }
    }

    async function excluirUsuario(cpf) {
        var response = await fetch("/api/usuarios/" + encodeURIComponent(cpf), {
            method: "DELETE",
            credentials: "same-origin",
        });
        var result = await response.json().catch(function () { return {}; });
        if (result.status === "ok") {
            carregarUsuarios();
        } else {
            alert(result.message || "Erro ao excluir.");
        }
    }

    async function alternarStatus(cpf, ativo) {
        var response = await fetch("/api/usuarios/" + encodeURIComponent(cpf), {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ ativo: ativo }),
            credentials: "same-origin",
        });
        var result = await response.json().catch(function () { return {}; });
        if (result.status === "ok") {
            carregarUsuarios();
        } else {
            alert(result.message || "Erro ao alterar status.");
        }
    }

    document.addEventListener("DOMContentLoaded", function () {
        modalUsuario = new bootstrap.Modal(document.getElementById("modal_usuario"));
        modalSenha = new bootstrap.Modal(document.getElementById("modal_senha"));

        carregarSessao();

        document.getElementById("btn_novo_usuario").addEventListener("click", abrirModalCriar);
        document.getElementById("btn_salvar_usuario").addEventListener("click", salvarUsuario);
        document.getElementById("btn_salvar_senha").addEventListener("click", redefinirSenha);
        document.getElementById("btn_salvar_meus_dados").addEventListener("click", salvarMeusDados);

        document.getElementById("pesquisa_usuario").addEventListener("input", function () {
            carregarUsuarios(this.value.trim());
        });

        document.getElementById("usuario_cpf_visual").addEventListener("input", function () {
            this.value = aplicarMascaraCPF(this.value);
        });

        document.getElementById("meu_dn").addEventListener("input", function () {
            var digits = this.value.replace(/\D/g, "").slice(0, 8);
            var formatted = "";
            if (digits.length > 0) {
                formatted += digits.slice(0, 2);
            }
            if (digits.length >= 3) {
                formatted += "/" + digits.slice(2, 4);
            }
            if (digits.length >= 5) {
                formatted += "/" + digits.slice(4, 8);
            }
            this.value = formatted;
        });
    });
})();
