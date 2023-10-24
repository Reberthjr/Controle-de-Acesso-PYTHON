import datetime
import tkinter as tk
from tkinter import ttk, END, NO, messagebox
from tkinter.ttk import Treeview, Combobox
import customtkinter as ctk
import pyodbc

# Função para centralizar a janela
def centralizar_janela(janela, largura, altura):
    largura_janela = largura
    altura_janela = altura
    x_pos = int((janela.winfo_screenwidth() / 2) - (largura_janela / 2))
    y_pos = int((janela.winfo_screenheight() / 2) - (altura_janela / 2))
    janela.geometry(f"{largura_janela}x{altura_janela}+{x_pos}+{y_pos}")

try:
    # Fazendo conexão com o banco de dados
    dados_conexao = ("Driver={SQL Server};"
                     "Server=;"
                     "PORT=;"
                     "Database=;"
                     "UID=;"
                     "PWD="
                     )
    conexao = pyodbc.connect(dados_conexao)
    cursor = conexao.cursor()

except pyodbc.Error as err:
    print(f'Erro encontrado {err}')

NomeResgatado = None

def sistema():


    def logoff():
        # Implemente aqui a lógica para fazer logoff
        pass

    def abrir_janela_cadastro():
        janela_cadastro = ctk.CTk()
        janela_cadastro.title("Cadastro")

        # Adicione os elementos de interface para o cadastro aqui
        # (combobox, campo em branco, tabela, etc.)

        # Centralize a janela de cadastro
        centralizar_janela(janela_cadastro, largura, altura)

        janela_cadastro.mainloop()

    registros = []

    # Função adicionar registros
    def adicionar_registro():
        nome_usuario = NomeResgatado
        nome_operador = nome_operador_entry.get()
        id_terminal = id_terminal_combobox.get()
        id_bip = id_bip_combobox.get()
        status = status_combobox.get()

        # Verifica se algum campo obrigatório está em branco
        if nome_operador == '' or id_terminal == '' or id_bip == '' or status == '':
            print("Por favor, preencha todos os campos antes de adicionar o registro.")
            messagebox.showerror("Informações incompletas", "Algumas informações estão faltando. Por favor, preencha todos os campos e tente novamente.")
            return

        # Pega data e hora atual
        registro_datetime = datetime.datetime.now()
        data_hora_formatada = registro_datetime

        try:
            # Insere os dados na tabela 'registros'
            cursor.execute(
                "INSERT INTO registros (nome_usuario, nome_operador, Id_terminal, Id_bip, status, Hora_registro) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (nome_usuario, nome_operador, id_terminal, id_bip, status, data_hora_formatada))
            conexao.commit()
            registros.append((nome_usuario, nome_operador, id_terminal, id_bip, status, data_hora_formatada))
            atualizar_tabela()
            print("Registro inserido com sucesso.")
        except pyodbc.Error as err:
            print(f'Erro ao inserir registro: {err}')

        # Limpa os campos após adicionar o registro
        nome_operador_entry.delete(0, 'end')
        id_terminal_combobox.set('')  # Limpar a combobox
        id_bip_combobox.set('')  # Limpar a combobox
        status_combobox.set('')  # Limpar a combobox

    # Função para atualizar a tabela
    def atualizar_tabela():
        # Limpar a tabela atual
        tree.delete(*tree.get_children())

        # Calcular a data e hora de 12 horas atrás
        doze_horas_atras = datetime.datetime.now() - datetime.timedelta(hours=12)
        formato = "%Y-%m-%d %H:%M:%S"
        data_hora_doze_horas_atras = doze_horas_atras

        # Preencher a tabela com os registros das últimas 12 horas
        ComandoMostrar = f"""SELECT nome_usuario, nome_operador, Id_terminal, Id_bip, status, Hora_registro FROM registros WHERE Hora_registro >= ?"""
        cursor.execute(ComandoMostrar, (data_hora_doze_horas_atras,))

        for row in cursor.fetchall():
            # Formate os valores antes de inseri-los na tabela
            formatted_row = tuple(str(value) for value in row)
            registros.append(formatted_row)
            tree.insert("", "end", values=formatted_row)

    # Função para buscar terminais com status disponível
    def buscar_terminais_disponiveis():
        terminais_disponiveis = []

        try:
            # Consulta para buscar os IDs dos terminais com status 'disponivel'
            cursor.execute("SELECT * FROM terminais WHERE status = 'disponivel'")
            rows = cursor.fetchall()

            # Adicionar os IDs dos terminais disponíveis à lista 'terminais_disponiveis'
            for row in rows:
                terminais_disponiveis.append(row[0])

            return terminais_disponiveis
        except pyodbc.Error as err:
            print(f'Erro ao buscar terminais disponíveis: {err}')
            return []

    # Janela editar bipes
    def abrirJanelaEditar():
        def on_table_click(event):
            id_bip_entry.delete(0, END)
            # Obtenha a linha e coluna clicadas na tabela
            item = tabela.item(tabela.selection())
            row = item['values']
            print(row[0])

            # Preencha os campos Entry com os valores da linha selecionada
            id_bip_entry.insert(0, row[0])

        def editar_bip():
            # SELECIONA UM ITEM, DENTRO DA TABELA
            itemSelecionado = tabela.selection()[0]

            # SELECIONA UM VALOR DENTRO DA TABELA
            valores = tabela.item(itemSelecionado, "values")

            print(valores[0])
            valor = messagebox.askquestion(title='Confirmação', message='Os dados estão corretos?')

            if valor == 'yes':
                InserirEdicao = f"""UPDATE bips SET status = '{status_combobox.get()}' WHERE tag_bip = '{valores[0]}'"""
                cursor.execute(InserirEdicao)
                cursor.commit()

                exibirTudo = """SELECT tag_bip FROM bips WHERE status ='disponivel'"""
                cursor.execute(exibirTudo)
                linhaEditar = cursor.fetchall()
                contador = 0
                dados = []
                for linha in linhaEditar:
                    dados.append(linhaEditar[contador][0])
                    contador += 1
                id_bip_combobox['values'] = dados

                janela_editar_bips.destroy()
            elif valor == 'no':
                janela_editar_bips.focus_force()

        janela_editar_bips = ctk.CTk()
        janela_editar_bips.title("Editar Bips")

        # Exemplo de campo de ID do Bip
        id_bip_label = ctk.CTkLabel(janela_editar_bips, text="TAG do Bip:")
        id_bip_label.grid(row=0, column=0, padx=10, pady=5, sticky='e')
        id_bip_entry = ctk.CTkEntry(janela_editar_bips)
        id_bip_entry.grid(row=0, column=1, padx=10, pady=5, sticky='w')

        # Exemplo de campo de Status do Bip
        status_label = ctk.CTkLabel(janela_editar_bips, text="Status do Bip:")
        status_label.grid(row=1, column=0, padx=10, pady=5, sticky='e')
        status_combobox = Combobox(janela_editar_bips, values=["Disponivel", "Defeito"], state="readonly")
        status_combobox.grid(row=1, column=1, padx=10, pady=5, sticky='w')

        # Botão para confirmar a edição
        editar_button = ctk.CTkButton(janela_editar_bips, text="Editar", command=editar_bip)
        editar_button.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

        # Centralize o conteúdo na janela
        tabela = ttk.Treeview(janela_editar_bips, select='browse', columns=('column1', 'column2'), show='headings')
        tabela.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

        tabela.column('column1', width=200, minwidth=50, stretch=NO)
        tabela.heading('#1', text='TAG_bip')

        tabela.column('column2', width=200, minwidth=50, stretch=NO)
        tabela.heading('#2', text='Status')
        tabela.bind("<ButtonRelease-1>", on_table_click)

        exibirTudo = """SELECT tag_bip, status FROM bips"""
        cursor.execute(exibirTudo)
        linha = cursor.fetchall()

        i = 0
        for linhas in linha:
            tabela.insert("", END, values=(linha[i][0], linha[i][1]))
            i += 1

        for child in janela_editar_bips.winfo_children():
            child.grid_configure(padx=10, pady=5)

        # Centralize a janela de edição de bips
        largura = 400
        altura = 300
        centralizar_janela(janela_editar_bips, largura, altura)

        janela_editar_bips.mainloop()

    #Janela editar terminais

    def abrirJanelaEditarTerminais():
        def on_table_click(event):
            id_terminal_entry.delete(0, END)
            # Obtenha a linha e coluna clicadas na tabela
            item = tabela.item(tabela.selection())
            row = item['values']
            print(row[0])

            # Preencha os campos Entry com os valores da linha selecionada
            id_terminal_entry.insert(0, row[0])

        def editar_terminal():
            # SELECIONA UM ITEM, DENTRO DA TABELA
            itemSelecionado = tabela.selection()[0]

            # SELECIONA UM VALOR DENTRO DA TABELA
            valores = tabela.item(itemSelecionado, "values")

            print(valores[0])
            valor = messagebox.askquestion(title='Confirmação', message='Os dados estão corretos?')

            if valor == 'yes':
                InserirEdicao = f"""UPDATE terminais SET status = '{status_combobox.get()}' WHERE tag_terminal = '{valores[0]}'"""
                cursor.execute(InserirEdicao)
                cursor.commit()

                exibirTudo = """SELECT tag_terminal FROM terminais WHERE status ='disponivel'"""
                cursor.execute(exibirTudo)
                linhaEditar = cursor.fetchall()
                contador = 0
                dados = []
                for linha in linhaEditar:
                    dados.append(linhaEditar[contador][0])
                    contador += 1
                id_terminal_combobox['values'] = dados

                janela_editar_terminais.destroy()
            elif valor == 'no':
                janela_editar_terminais.focus_force()

        janela_editar_terminais = ctk.CTk()
        janela_editar_terminais.title("Editar Terminais")

        # Exemplo de campo de ID do Terminal
        id_terminal_label = ctk.CTkLabel(janela_editar_terminais, text="Tag do Terminal:")
        id_terminal_label.grid(row=0, column=0, padx=10, pady=5, sticky='e')
        id_terminal_entry = ctk.CTkEntry(janela_editar_terminais)
        id_terminal_entry.grid(row=0, column=1, padx=10, pady=5, sticky='w')

        # Exemplo de campo de Status do Terminal
        status_label = ctk.CTkLabel(janela_editar_terminais, text="Status do Terminal:")
        status_label.grid(row=1, column=0, padx=10, pady=5, sticky='e')
        status_combobox = Combobox(janela_editar_terminais, values=["Disponivel", "Em uso", "Defeito"],
                                   state="readonly")
        status_combobox.grid(row=1, column=1, padx=10, pady=5, sticky='w')

        # Botão para confirmar a edição
        editar_button = ctk.CTkButton(janela_editar_terminais, text="Editar", command=editar_terminal)
        editar_button.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

        # Centralize o conteúdo na janela
        tabela = ttk.Treeview(janela_editar_terminais, select='browse', columns=('column1', 'column2'), show='headings')
        tabela.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

        tabela.column('column1', width=200, minwidth=50, stretch=NO)
        tabela.heading('#1', text='Tag_terminal')

        tabela.column('column2', width=200, minwidth=50, stretch=NO)
        tabela.heading('#2', text='Status')
        tabela.bind("<ButtonRelease-1>", on_table_click)

        exibirTudo = """SELECT tag_terminal, status FROM terminais"""
        cursor.execute(exibirTudo)
        linha = cursor.fetchall()

        i = 0
        for linhas in linha:
            tabela.insert("", END, values=(linha[i][0], linha[i][1]))
            i += 1

        for child in janela_editar_terminais.winfo_children():
            child.grid_configure(padx=10, pady=5)

        # Centralize a janela de edição de terminais
        largura = 400
        altura = 300
        centralizar_janela(janela_editar_terminais, largura, altura)

        janela_editar_terminais.mainloop()

    # Criação da janela principal usando CustomTkinter
    root = ctk.CTk()
    root.title('Página Principal')

    # Crie uma variável para a largura e altura da janela principal
    largura = 1366
    altura = 768

    # Centralize a janela principal
    centralizar_janela(root, largura, altura)

    # Criação da tabela de registro
    columns = ("Nome do Usuário", "Nome do Operador", "TAG do Terminal", "TAG do Bip", "Status", "Hora de Registro")
    tree = Treeview(root, columns=columns, show="headings")

    for col in columns:
        tree.heading(col, text=col)

    tree.pack()

    # Atualizar a tabela com os registros das últimas 12 horas
    atualizar_tabela()

    # Formulário para adicionar registro
    form_frame = ctk.CTkFrame(root)
    form_frame.pack(pady=10)

    nome_pessoa_label = ctk.CTkLabel(form_frame, text=f"Nome do usuário")
    nome_pessoa_label.grid(row=0, column=0)
    nome_pessoa_entry = ctk.CTkLabel(form_frame, text=f'{NomeResgatado}')
    nome_pessoa_entry.grid(row=0, column=1)

    nome_operador_label = ctk.CTkLabel(form_frame, text="Nome do Operador:")
    nome_operador_label.grid(row=1, column=0)
    nome_operador_entry = ctk.CTkEntry(form_frame)
    nome_operador_entry.grid(row=1, column=1)

    id_terminal_label = ctk.CTkLabel(form_frame, text="TAG do Terminal:")
    id_terminal_label.grid(row=2, column=0)
    id_terminal_label = buscar_terminais_disponiveis()
    id_terminal_combobox = Combobox(form_frame, values=id_terminal_label, state="readonly")
    id_terminal_combobox.grid(row=2, column=1)

    # Combobox bip disponivel
    id_bip_label = ctk.CTkLabel(form_frame, text="TAG do Bip:")
    id_bip_label.grid(row=3, column=0)
    exibirTudo = """Select * from bips where status ='disponivel'"""
    cursor.execute(exibirTudo)
    linhaEditar = cursor.fetchall()
    contador = 0
    dados = []
    for linha in linhaEditar:
        dados.append(linhaEditar[contador][0])
        contador += 1


    id_bip_combobox = Combobox(form_frame, values=(dados), state="readonly")
    id_bip_combobox.grid(row=3, column=1)

    status_label = ctk.CTkLabel(form_frame, text="Status (Entrada/Saída):")
    status_label.grid(row=5, column=0)
    status_combobox = Combobox(form_frame, values=["Entrada", "Saída"], state="readonly")
    status_combobox.grid(row=5, column=1)

    adicionar_button = ctk.CTkButton(form_frame, text="Registrar", command=adicionar_registro)
    adicionar_button.grid(row=6, column=0, columnspan=2, padx=10, pady=10)

    botao_editar_bips = ctk.CTkButton(form_frame, text="Editar Bips", command=abrirJanelaEditar)
    botao_editar_bips.grid(row=12, column=0, columnspan=2, padx=10, pady=10)

    botao_editar_terminais = ctk.CTkButton(form_frame, text="Editar Terminais", command=abrirJanelaEditarTerminais)
    botao_editar_terminais.grid(row=15, column=0, columnspan=4, padx=10, pady=10)

    # Iniciar a interface gráfica
    root.mainloop()

# Função de login
def acessar():
    global NomeResgatado
    consulta = f"""SELECT * FROM login WHERE usuario = '{EntryUser.get()}'"""
    cursor.execute(consulta)
    consultar = cursor.fetchall()

    if consultar and EntryUser.get() == consultar[0][0] and EntryPass.get() == consultar[0][1]:
        # Passa o nome de usuário para a função sistema
        NomeResgatado = consultar[0][0]
        JanelaLogin.destroy()
        sistema()
    else:
        # Exibir um alerta de senha errada em um popup
        messagebox.showerror("Credenciais incorretas", "Usuario ou senha incorretos. Por favor, tente novamente.")

def acionar_com_enter(event):
    acessar()

JanelaLogin = ctk.CTk()
JanelaLogin.geometry('400x400')

UserLabel = ctk.CTkLabel(JanelaLogin, text='Login')
UserLabel.place(relx=0.1, rely=0.1, anchor='center')
EntryUser = ctk.CTkEntry(JanelaLogin)
EntryUser.place(relx=0.25, rely=0.2, anchor='center')

PassLabel = ctk.CTkLabel(JanelaLogin, text='Password')
PassLabel.place(relx=0.1, rely=0.4, anchor='center')
EntryPass = ctk.CTkEntry(JanelaLogin, show='*')
EntryPass.place(relx=0.25, rely=0.5, anchor='center')

btnAcesso = ctk.CTkButton(JanelaLogin, text='acessar', command=acessar)
btnAcesso.place(relx=0.2, rely=0.65, anchor='center')
JanelaLogin.bind("<Return>", acionar_com_enter)
# Centralize a janela de login
largura = 400
altura = 400
centralizar_janela(JanelaLogin, largura, altura)

JanelaLogin.mainloop()