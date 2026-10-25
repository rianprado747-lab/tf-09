# Os pilares na árvore de arquivos: herança, polimorfismo, abstração e interface.
# Rodar no terminal: python3 pilares.py
#
# O Item da Aula 08 tinha um booleano (eh_pasta) e vários "if eh_pasta".
# Aqui ele vira três classes: Item (o geral), Pasta e Arquivo (os específicos),
# e quem usa a árvore deixa de perguntar "você é pasta?".
from abc import ABC, abstractmethod


# INTERFACE: contrato puro, sem estado e sem implementação.
# Quem assina promete saber dizer o próprio tamanho em bytes.
class Medivel(ABC):
    __slots__ = ()

    @abstractmethod
    def tamanho(self):
        pass


# ABSTRAÇÃO + HERANÇA: o que toda pasta e todo arquivo têm em comum.
# Não dá para criar um Item "solto": ele é só o recorte do essencial.
class Item(Medivel):
    __slots__ = ("__nome", "__pai")

    def __init__(self, nome, pai=None):
        self.__validar_nome(nome)
        self.__nome = nome
        self.__pai = None

        if pai is not None:
            self.mover_para(pai)

    def __validar_nome(self, nome):
        if nome == "" or "/" in nome:
            raise ValueError("nome inválido: " + repr(nome))

    @property
    def nome(self):
        return self.__nome

    @nome.setter
    def nome(self, novo_nome):
        self.__validar_nome(novo_nome)
        self.__nome = novo_nome

    @property
    def pai(self):
        return self.__pai

    def mover_para(self, destino):
        if destino is self.__pai:
            return

        destino._receber(self)          # cada tipo decide se aceita
        if self.__pai is not None:
            self.__pai._soltar(self)
        self.__pai = destino

    # PROTEGIDO: o gancho que as filhas sobrescrevem. Por padrão, recusa.
    def _receber(self, item):
        raise ValueError(self.__nome + " é um arquivo, não pode conter itens")

    def caminho(self):
        if self.__pai is None:
            return self.__nome
        return self.__pai.caminho() + "/" + self.__nome

    def profundidade(self):
        if self.__pai is None:
            return 0
        return self.__pai.profundidade() + 1

    @abstractmethod
    def mostrar(self):
        pass


class Arquivo(Item):
    __slots__ = ("__bytes",)

    def __init__(self, nome, tamanho_bytes, pai=None):
        if tamanho_bytes < 0:
            raise ValueError("tamanho não pode ser negativo")
        self.__bytes = tamanho_bytes
        super().__init__(nome, pai)

    def tamanho(self):
        return self.__bytes

    def mostrar(self):
        recuo = "    " * self.profundidade()
        print(recuo + self.nome + " (" + str(self.tamanho()) + " B)")


class Pasta(Item):
    __slots__ = ("__filhos",)

    def __init__(self, nome, pai=None):
        self.__filhos = []
        super().__init__(nome, pai)

    @property
    def filhos(self):
        return tuple(self.__filhos)

    # OVERRIDE do gancho protegido: a pasta aceita, desde que não crie um ciclo.
    def _receber(self, item):
        ancestral = self
        while ancestral is not None:
            if ancestral is item:
                raise ValueError("não dá para mover " + item.nome + " para dentro dela mesma")
            ancestral = ancestral.pai
        self.__filhos.append(item)

    def _soltar(self, item):
        self.__filhos.remove(item)

    # POLIMORFISMO: a pasta soma o que tem dentro; nenhum filho é perguntado
    # se é pasta ou arquivo, cada um responde do seu jeito.
    def tamanho(self):
        total = 0
        for filho in self.__filhos:
            total = total + filho.tamanho()
        return total

    def mostrar(self):
        recuo = "    " * self.profundidade()
        print(recuo + self.nome + "/ (" + str(self.tamanho()) + " B)")
        for filho in self.__filhos:
            filho.mostrar()


# Outra classe que assina o contrato SEM ser da árvore: a Lixeira.
class Lixeira(Medivel):
    __slots__ = ("__descartados",)

    def __init__(self):
        self.__descartados = []

    def descartar(self, arquivo):
        self.__descartados.append(arquivo)

    def tamanho(self):
        total = 0
        for arquivo in self.__descartados:
            total = total + arquivo.tamanho()
        return total
# Clase atalho 
class Atalho(Item):
    __slots__ = ('__destino',)

    def __init__(self, nome, destino, pai = None):
        super().__init__(nome,pai)
        self.redirecionar(destino)

    @property
    def destino(self):
        return self.__destino


    def redirecionar(self, novo_destino):
        if novo_destino is self:
            raise ValueError('O atalho não pode apontar para ele mesmo')

        ancestral = self.pai
        while ancestral is not None:
            if ancestral is novo_destino:
                raise ValueError('O destino não pode ser uma pasta que contém o atalho')
            ancestral = ancestral.pai

        self.__destino = novo_destino


    def tamanho(self):
        return 1


    def mostrar(self):
        recuo = '   ' * self.profundidade()
        print(recuo + self.nome + " -> " + self.destino.caminho())

# Quem usa o contrato não sabe (nem quer saber) quem está do outro lado.
def espaco_total(coisas):
    total = 0
    for coisa in coisas:
        total = total + coisa.tamanho()
    return total


def tentar(rotulo, acao):
    try:
        acao()
        print(rotulo, "-> passou (!)")
    except Exception as erro:
        print(rotulo, "->", type(erro).__name__ + ":", erro)


disco = Pasta("C:")
usuarios = Pasta("Users", disco)
rian = Pasta("Rian Prado", usuarios)
desktop = Pasta("Desktop", rian)
documentos = Pasta("Documentos", rian)

texto = Arquivo("anotacoes.txt", 300, desktop)
foto = Arquivo("perfil.png", 2000, rian)

atalho_foto = Atalho("atalho_foto.lnk", foto, desktop)
atalho_docs = Atalho("atalho_docs.lnk", documentos, desktop)


print("\n--- ÁRVORE COMPLETA ---")
disco.mostrar()


lixeira = Lixeira()
lixeira.descartar(Arquivo("temp.tmp", 150))

print("\n--- ESPAÇO TOTAL ---")
# O arquivo 'texto' tem 300 bytes.
# A pasta 'desktop' tem o arquivo 'texto' (300) + atalho_foto (1) + atalho_usuarios (1) = 302 bytes.
# A 'lixeira' tem 150 bytes.
# Total esperado: 300 + 302 + 150 = 752 bytes.
lista_de_coisas = [texto, desktop, lixeira]
print("Total calculado:", espaco_total(lista_de_coisas), "bytes")

# 4. Três tentativas que precisam falhar (validações do Atalho)
print("\n--- TENTATIVAS DE QUEBRA ---")

# Falha 1: Tentar alterar o destino usando o sinal de igual (encapsulamento sem setter)
tentar("Mudar destino com '='", lambda: setattr(atalho_foto, "destino", texto))

# Falha 2: Tentar fazer o atalho apontar para ele mesmo
tentar("Atalho apontar para si", lambda: atalho_foto.redirecionar(atalho_foto))

# Falha 3: Tentar fazer o atalho apontar para uma pasta que já o contém (ancestral)
tentar("Atalho apontar para o avô (Users)", lambda: atalho_foto.redirecionar(usuarios))
