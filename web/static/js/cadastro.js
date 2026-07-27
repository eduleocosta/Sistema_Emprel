document.addEventListener("DOMContentLoaded", function () {
    verificarSessao();
    carregarCadastros();
    carregarAcoes();
    carregarServicos();
    carregarVans();

    document.getElementById("btn_add_tel").addEventListener("click", function () {
        var container = document.getElementById("tel_extra_container");
        var existing = container.querySelectorAll(".tel-extra").length;
        if (existing === 0) {
            var div = document.createElement("div");
            div.className = "input-group mb-2 mt-2 tel-extra";
            div.innerHTML = '<input type="text" class="form-control tel-extra-input" placeholder="Telefone extra">';
            container.appendChild(div);
            this.textContent = "-";
            this.classList.remove("btn-outline-success");
            this.classList.add("btn-outline-danger");
        } else {
            container.innerHTML = "";
            this.textContent = "+";
            this.classList.remove("btn-outline-danger");
            this.classList.add("btn-outline-success");
        }
    });

    document.getElementById("chk_sem_tel").addEventListener("change", function () {
        var telInput = document.getElementById("ent_tel");
        var btnAdd = document.getElementById("btn_add_tel");
        if (this.checked) {
            telInput.value = "";
            telInput.disabled = true;
            btnAdd.disabled = true;
        } else {
            telInput.disabled = false;
            btnAdd.disabled = false;
        }
    });

    document.getElementById("btn_salvar").addEventListener("click", function () {
        salvarCadastro();
    });

    document.getElementById("btn_excluir").addEventListener("click", function () {
        excluirCadastro();
    });

    document.getElementById("btn_limpar").addEventListener("click", function () {
        limparCampos();
    });

    document.getElementById("btn_selecionar_acao_servico").addEventListener("click", function () {
        var acao = document.getElementById("ent_acao").value;
        var servico = document.getElementById("ent_servico").value;
        if (!acao || !servico) {
            alert("Selecione a ação e o serviço");
            return;
        }
        document.getElementById("ent_acao").value = acao;
        document.getElementById("ent_servico").value = servico;
    });

    document.getElementById("btn_pesquisar").addEventListener("click", function () {
        pesquisarCadastro();
    });

    document.getElementById("pesquisa_protocolo").addEventListener("keyup", function (e) {
        if (e.key === "Enter") {
            pesquisarCadastro();
        }
    });

    document.getElementById("ent_cpf").addEventListener("input", function () {
        var val = this.value.replace(/\D/g, "");
        if (val.length > 11) val = val.slice(0, 11);
        if (val.length <= 3) {
            this.value = val;
        } else if (val.length <= 6) {
            this.value = val.slice(0, 3) + "." + val.slice(3);
        } else if (val.length <= 9) {
            this.value = val.slice(0, 3) + "." + val.slice(3, 6) + "." + val.slice(6);
        } else {
            this.value = val.slice(0, 3) + "." + val.slice(3, 6) + "." + val.slice(6, 9) + "-" + val.slice(9);
        }
    });

    document.getElementById("ent_tel").addEventListener("input", function () {
        var val = this.value.replace(/\D/g, "");
        if (val.length > 11) val = val.slice(0, 11);
        if (val.length <= 2) {
            this.value = val;
        } else if (val.length <= 7) {
            this.value = "(" + val.slice(0, 2) + ") " + val.slice(2);
        } else {
            this.value = "(" + val.slice(0, 2) + ") " + val.slice(2, 7) + "-" + val.slice(7);
        }
    });

    document.getElementById("ent_data").addEventListener("input", function () {
        var val = this.value.replace(/\D/g, "");
        if (val.length > 8) val = val.slice(0, 8);
        if (val.length > 2) {
            this.value = val.slice(0, 2) + "/" + val.slice(2);
        }
        if (val.length > 4) {
            this.value = val.slice(0, 2) + "/" + val.slice(2, 4) + "/" + val.slice(4);
        }
    });
});

function verificarSessao() {
    fetch("/api/session")
        .then(function (r) { return r.json(); })
        .then(function (data) {
            if (!data.logged) {
                window.location.href = "/login";
            }
        });
}

function logout() {
    fetch("/api/logout", { method: "POST" })
        .then(function () {
            window.location.href = "/login";
        });
}

document.getElementById("btn_logout").addEventListener("click", function (e) {
    e.preventDefault();
    logout();
});

    document.getElementById("btn_add_tel").addEventListener("click", function () {
        var container = document.getElementById("tel_extra_container");
        var existing = container.querySelectorAll(".tel-extra").length;
        if (existing === 0) {
            var div = document.createElement("div");
            div.className = "input-group mb-2 mt-2 tel-extra";
            div.innerHTML = '<input type="text" class="form-control tel-extra-input" placeholder="Telefone extra">';
            container.appendChild(div);
            this.textContent = "-";
            this.classList.remove("btn-outline-success");
            this.classList.add("btn-outline-danger");
        } else {
            container.innerHTML = "";
            this.textContent = "+";
            this.classList.remove("btn-outline-danger");
            this.classList.add("btn-outline-success");
        }
    });

    document.getElementById("chk_sem_tel").addEventListener("change", function () {
        var telInput = document.getElementById("ent_tel");
        var btnAdd = document.getElementById("btn_add_tel");
        if (this.checked) {
            telInput.value = "";
            telInput.disabled = true;
            btnAdd.disabled = true;
        } else {
            telInput.disabled = false;
            btnAdd.disabled = false;
        }
    });

    document.getElementById("btn_salvar").addEventListener("click", function () {
        salvarCadastro();
    });

    document.getElementById("btn_excluir").addEventListener("click", function () {
        excluirCadastro();
    });

    document.getElementById("btn_limpar").addEventListener("click", function () {
        limparCampos();
    });

    document.getElementById("btn_selecionar_acao_servico").addEventListener("click", function () {
        var acao = document.getElementById("ent_acao").value;
        var servico = document.getElementById("ent_servico").value;
        if (!acao || !servico) {
            alert("Selecione a ação e o serviço");
            return;
        }
        document.getElementById("ent_acao").value = acao;
        document.getElementById("ent_servico").value = servico;
    });

    document.getElementById("btn_pesquisar").addEventListener("click", function () {
        pesquisarCadastro();
    });

    document.getElementById("pesquisa_protocolo").addEventListener("keyup", function (e) {
        if (e.key === "Enter") {
            pesquisarCadastro();
        }
    });

    document.getElementById("ent_cpf").addEventListener("input", function () {
        var val = this.value.replace(/\D/g, "");
        if (val.length > 11) val = val.slice(0, 11);
        if (val.length <= 3) {
            this.value = val;
        } else if (val.length <= 6) {
            this.value = val.slice(0, 3) + "." + val.slice(3);
        } else if (val.length <= 9) {
            this.value = val.slice(0, 3) + "." + val.slice(3, 6) + "." + val.slice(6);
        } else {
            this.value = val.slice(0, 3) + "." + val.slice(3, 6) + "." + val.slice(6, 9) + "-" + val.slice(9);
        }
    });

    document.getElementById("ent_tel").addEventListener("input", function () {
        var val = this.value.replace(/\D/g, "");
        if (val.length > 11) val = val.slice(0, 11);
        if (val.length <= 2) {
            this.value = val;
        } else if (val.length <= 7) {
            this.value = "(" + val.slice(0, 2) + ") " + val.slice(2);
        } else {
            this.value = "(" + val.slice(0, 2) + ") " + val.slice(2, 7) + "-" + val.slice(7);
        }
    });

    document.getElementById("ent_data").addEventListener("input", function () {
        var val = this.value.replace(/\D/g, "");
        if (val.length > 8) val = val.slice(0, 8);
        if (val.length > 2) {
            this.value = val.slice(0, 2) + "/" + val.slice(2);
        }
        if (val.length > 4) {
            this.value = val.slice(0, 2) + "/" + val.slice(2, 4) + "/" + val.slice(4);
        }
    });
});

function pesquisarCadastro() {
    var protocolo = document.getElementById("pesquisa_protocolo").value.trim();
    var url = "/api/cadastros";
    if (protocolo) {
        url = "/api/cadastros/pesquisar?protocolo=" + encodeURIComponent(protocolo);
    }
    fetch(url)
        .then(function (r) { return r.json(); })
        .then(function (data) {
            var tbody = document.getElementById("tbody_cadastros");
            tbody.innerHTML = "";
            data.forEach(function (item) {
                var tr = document.createElement("tr");
                tr.innerHTML =
                    "<td>" + escapeHtml(item.protocolo || "") + "</td>" +
                    "<td>" + escapeHtml(item.cpf || "") + "</td>" +
                    "<td>" + escapeHtml(item.nome || "") + "</td>" +
                    "<td>" + escapeHtml(item.telefone || "") + "</td>" +
                    "<td>" + escapeHtml(item.data || "") + "</td>" +
                    "<td>" + escapeHtml(item.acao || "") + "</td>" +
                    "<td>" + escapeHtml(item.servico || "") + "</td>" +
                    "<td><button class='btn btn-sm btn-warning btn-editar' data-id='" + item.id + "'>Editar</button> " +
                    "<button class='btn btn-sm btn-danger btn-excluir' data-id='" + item.id + "'>Excluir</button></td>";
                tbody.appendChild(tr);
            });
            bindEditButtons();
            bindDeleteButtons();
        });
}

function carregarCadastros() {
    fetch("/api/cadastros")
        .then(function (r) { return r.json(); })
        .then(function (data) {
            var tbody = document.getElementById("tbody_cadastros");
            tbody.innerHTML = "";
            data.forEach(function (item) {
                var tr = document.createElement("tr");
                tr.innerHTML =
                    "<td>" + escapeHtml(item.protocolo || "") + "</td>" +
                    "<td>" + escapeHtml(item.cpf || "") + "</td>" +
                    "<td>" + escapeHtml(item.nome || "") + "</td>" +
                    "<td>" + escapeHtml(item.telefone || "") + "</td>" +
                    "<td>" + escapeHtml(item.data || "") + "</td>" +
                    "<td>" + escapeHtml(item.acao || "") + "</td>" +
                    "<td>" + escapeHtml(item.servico || "") + "</td>" +
                    "<td><button class='btn btn-sm btn-warning btn-editar' data-id='" + item.id + "'>Editar</button> " +
                    "<button class='btn btn-sm btn-danger btn-excluir' data-id='" + item.id + "'>Excluir</button></td>";
                tbody.appendChild(tr);
            });
            bindEditButtons();
            bindDeleteButtons();
        });
}

function bindEditButtons() {
    document.querySelectorAll(".btn-editar").forEach(function (btn) {
        btn.addEventListener("click", function () {
            editarCadastro(this.getAttribute("data-id"));
        });
    });
}

function bindDeleteButtons() {
    document.querySelectorAll(".btn-excluir").forEach(function (btn) {
        btn.addEventListener("click", function () {
            excluirCadastroId(this.getAttribute("data-id"));
        });
    });
}

function carregarAcoes() {
    fetch("/api/acoes")
        .then(function (r) { return r.json(); })
        .then(function (data) {
            var select = document.getElementById("ent_acao");
            select.innerHTML = '<option value="">Selecionar...</option>';
            data.forEach(function (a) {
                var opt = document.createElement("option");
                opt.value = a.id;
                opt.textContent = a.nome || a.local || a.id;
                select.appendChild(opt);
            });
        });
}

function carregarServicos() {
    fetch("/api/servicos")
        .then(function (r) { return r.json(); })
        .then(function (data) {
            var select = document.getElementById("ent_servico");
            select.innerHTML = '<option value="">Selecionar...</option>';
            data.forEach(function (s) {
                var opt = document.createElement("option");
                opt.value = s.id;
                opt.textContent = s.nome || s.id;
                select.appendChild(opt);
            });
        });
}

function carregarVans() {
    fetch("/api/vans")
        .then(function (r) { return r.json(); })
        .then(function (data) {
        });
}

function salvarCadastro() {
    var protocolo = document.getElementById("ent_protocolo").value.trim();
    var cpf = document.getElementById("ent_cpf").value.trim();
    var nome = document.getElementById("ent_nome").value.trim();
    var telefone = document.getElementById("ent_tel").value.trim();
    var data = document.getElementById("ent_data").value.trim();
    var acao = document.getElementById("ent_acao").value;
    var servico = document.getElementById("ent_servico").value;
    var semTel = document.getElementById("chk_sem_tel").checked;

    if (!protocolo || !nome) {
        alert("Preencha pelo menos o Protocolo e o Nome");
        return;
    }

    var telefoneValue = semTel ? "" : telefone;

    var dados = {
        protocolo: protocolo,
        cpf: cpf,
        nome: nome,
        telefone: telefoneValue,
        data: data,
        acao: acao,
        servico: servico,
    };

    fetch("/api/cadastros", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(dados),
    })
        .then(function (r) { return r.json(); })
        .then(function (result) {
            alert("Cadastro salvo com sucesso!");
            carregarCadastros();
            limparCampos();
        })
        .catch(function (err) {
            alert("Erro ao salvar: " + err.message);
        });
}

function editarCadastro(id) {
    fetch("/api/cadastros")
        .then(function (r) { return r.json(); })
        .then(function (data) {
            var item = data.find(function (c) { return String(c.id) === String(id); });
            if (!item) return;
            document.getElementById("ent_protocolo").value = item.protocolo || "";
            document.getElementById("ent_cpf").value = item.cpf || "";
            document.getElementById("ent_nome").value = item.nome || "";
            document.getElementById("ent_tel").value = item.telefone || "";
            document.getElementById("ent_data").value = item.data || "";
            document.getElementById("ent_acao").value = item.acao || "";
            document.getElementById("ent_servico").value = item.servico || "";
        });
}

function excluirCadastro() {
    var protocolo = document.getElementById("ent_protocolo").value.trim();
    if (!protocolo) {
        alert("Pesquise o cadastro que deseja excluir primeiro");
        return;
    }
    if (!confirm("Tem certeza que deseja excluir este cadastro?")) return;

    fetch("/api/cadastros")
        .then(function (r) { return r.json(); })
        .then(function (data) {
            var item = data.find(function (c) { return c.protocolo === protocolo; });
            if (!item) {
                alert("Cadastro não encontrado");
                return;
            }
            return fetch("/api/cadastros/" + item.id, { method: "DELETE" });
        })
        .then(function () {
            alert("Cadastro excluído com sucesso!");
            carregarCadastros();
            limparCampos();
        })
        .catch(function (err) {
            alert("Erro ao excluir: " + err.message);
        });
}

function excluirCadastroId(id) {
    if (!confirm("Tem certeza que deseja excluir este cadastro?")) return;
    fetch("/api/cadastros/" + id, { method: "DELETE" })
        .then(function () {
            alert("Cadastro excluído com sucesso!");
            carregarCadastros();
            limparCampos();
        })
        .catch(function (err) {
            alert("Erro ao excluir: " + err.message);
        });
}

function limparCampos() {
    document.getElementById("ent_protocolo").value = "";
    document.getElementById("ent_cpf").value = "";
    document.getElementById("ent_nome").value = "";
    document.getElementById("ent_tel").value = "";
    document.getElementById("ent_data").value = "";
    document.getElementById("ent_acao").value = "";
    document.getElementById("ent_servico").value = "";
    document.getElementById("chk_sem_tel").checked = false;
    document.getElementById("ent_tel").disabled = false;
    document.getElementById("btn_add_tel").disabled = false;
    document.getElementById("btn_add_tel").textContent = "+";
    document.getElementById("btn_add_tel").classList.remove("btn-outline-danger");
    document.getElementById("btn_add_tel").classList.add("btn-outline-success");
    document.getElementById("tel_extra_container").innerHTML = "";
}

function escapeHtml(text) {
    if (!text) return "";
    var div = document.createElement("div");
    div.appendChild(document.createTextNode(text));
    return div.innerHTML;
}