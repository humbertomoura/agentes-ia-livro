from fig import *

# 12.1 workflow da encomenda grande
fig,ax=canvas(9.6,4.2)
steps=[('Entender\no pedido',0.2),('Calcular\ningredientes',1.9),('Ver o\nforno',3.6),('Reservar\no forno',6.1),('Cobrar\no sinal',7.9)]
for t,x in steps: box(ax,x,2.3,1.35,0.95,t,fs=10)
box(ax,4.95,0.5,1.5,0.95,'Aprovação\nda Dona Cida',fc=LOR,ec=ORANGE,fs=10)
for a,b in [(1.55,1.9),(3.25,3.6),(7.45,7.9)]: arrow(ax,a,2.78,b,2.78)
arrow(ax,4.95,2.78,6.1,2.78,text='até R$ 1.000',fs=8.5)
arrow(ax,4.6,2.3,5.4,1.45,c=ORANGE,text='',fs=8.5)
ax.text(4.2,1.8,'acima de\nR$ 1.000',fontsize=8.5,color=ORANGE,ha='center')
arrow(ax,6.3,1.45,6.75,2.3,c=ORANGE); ax.text(6.95,1.75,'aprovado\n(esta versão)',fontsize=8.5,color=ORANGE)
ax.text(0.2,3.75,'Estado salvo a cada passo concluído',fontsize=10,color=TEAL,weight='bold')
for t,x in steps: ax.plot(x+0.675,3.42,marker='s',color=TEAL,ms=5)
ax.text(6.1,0.35,'Cancelou? Compensar: liberar o forno, estornar o sinal',fontsize=8.5,color=GRAY,style='italic')
save(fig,'f12_1.png')

# 14.1 formas de organizar a equipe
fig,ax=canvas(10.5,3.6)
def node(x,y,t,fc=LTEAL,ec=TEAL): box(ax,x-0.55,y-0.28,1.1,0.56,t,fc=fc,ec=ec,fs=8.5)
ax.text(1.85,3.3,'Supervisor',ha='center',fontsize=11,color=TEAL,weight='bold')
node(1.85,2.5,'Atendimento',LOR,ORANGE)
for x,t in [(0.65,'Produção'),(1.85,'Compras'),(3.05,'Pesquisa')]:
    node(x,1.1,t); arrow(ax,1.85,2.2,x,1.4)
ax.text(5.0,3.3,'Passagem de bastão',ha='center',fontsize=11,color=TEAL,weight='bold')
node(4.3,1.9,'Júlia\n(atendente)',LOR,ORANGE); node(5.7,1.9,'Seu Zé\n(bolos)')
arrow(ax,4.85,1.9,5.15,1.9); ax.text(5.0,1.2,'a conversa\nmuda de dono',ha='center',fontsize=8.5,color=GRAY)
ax.text(8.9,3.3,'Especialista como ferramenta',ha='center',fontsize=11,color=TEAL,weight='bold')
node(8.9,2.5,'Atendimento',LOR,ORANGE); node(8.9,1.1,'Compras')
arrow(ax,8.75,2.2,8.75,1.4,text=''); arrow(ax,9.05,1.4,9.05,2.2,c=TEAL)
ax.text(7.95,1.75,'pergunta',fontsize=8.5,color=GRAY); ax.text(9.2,1.75,'resumo',fontsize=8.5,color=TEAL)
ax.text(8.9,0.45,'o principal continua no comando',ha='center',fontsize=8.5,color=GRAY)
save(fig,'f14_1.png')

# 16.1 MCP
fig,ax=canvas(9,4)
ax.add_patch(FancyBboxPatch((0.2,0.4),3.6,3.2,boxstyle='round,pad=0.02,rounding_size=0.15',fc=LG,ec=GRAY,lw=1.2))
ax.text(2.0,3.3,'Host: sistema da padaria',ha='center',fontsize=10.5,color=DARK,weight='bold')
box(ax,0.5,1.7,1.3,1.1,'Agente\n+ modelo',fc=LOR,ec=ORANGE,fs=10)
for i,(y,t) in enumerate([(2.6,'Cliente 1'),(1.6,'Cliente 2'),(0.6,'Cliente 3')]):
    box(ax,2.2,y,1.3,0.6,t,fs=9.5)
    box(ax,5.6,y,3.1,0.6,['Servidor: agenda do forno','Servidor: estoque','Servidor: Pix do banco'][i],fs=9.5)
    arrow(ax,3.5,y+0.3,5.6,y+0.3,c=TEAL,text='MCP' if i==0 else None,fs=9)
    arrow(ax,1.8,2.25,2.2,y+0.3,c=GRAY)
save(fig,'f16_1.png')

# 17.1 A2A
fig,ax=canvas(9,4)
box(ax,0.2,1.5,2.0,1.1,'Agente de compras\n(padaria)',fc=LOR,ec=ORANGE,fs=10)
box(ax,6.8,1.5,2.0,1.1,'Agente do moinho',fs=10)
arrow(ax,2.2,2.35,6.8,2.35,c=GRAY,text='1. lê o cartão do agente e pede cotação',fs=8.5)
arrow(ax,6.8,1.95,2.2,1.95,c=TEAL,text='',fs=8.5)
states=['Enviada','Trabalhando','Precisa de\ninformação','Concluída']
for i,s in enumerate(states):
    box(ax,2.45+i*1.08,0.35,1.0,0.7,s,fc=LG if i<3 else LTEAL,ec=GRAY if i<3 else TEAL,fs=8)
    if i: arrow(ax,2.45+i*1.08-0.08,0.7,2.45+i*1.08,0.7)
ax.text(4.5,1.25,'2. a tarefa passa por estados; o resultado volta como artefato',ha='center',fontsize=8.5,color=TEAL)
ax.text(4.5,3.2,'Cada lado com suas regras: autenticação sempre, autoridade não viaja na mensagem',ha='center',fontsize=9,color=GRAY,style='italic')
save(fig,'f17_1.png')

# 21.1 WhatsApp
fig,ax=canvas(9,3)
items=[('Áudio da\ncliente',LG,GRAY),('Transcrição\n(incerta)',LG,GRAY),('Agente +\ncaderno',LTEAL,TEAL),('Confirmação\npor escrito',LOR,ORANGE),('Registrar a\nencomenda',LTEAL,TEAL)]
for i,(t,fc,ec) in enumerate(items):
    box(ax,0.15+i*1.8,1.1,1.45,0.95,t,fc=fc,ec=ec,fs=9.5)
    if i: arrow(ax,0.15+i*1.8-0.35,1.57,0.15+i*1.8,1.57)
ax.text(6.2,0.55,'a cliente responde "sim" antes de qualquer efeito',fontsize=8.5,color=ORANGE,ha='center')
ax.text(4.5,2.5,'O que mexe no mundo só acontece depois da confirmação por escrito',fontsize=10,color=TEAL,ha='center',weight='bold')
save(fig,'f21_1.png')

# 23.1 portão de regressão
fig,ax=canvas(9,3.6)
box(ax,0.2,1.3,1.8,1.0,'Mudança\n(prompt, modelo,\nferramenta)',fc=LG,ec=GRAY,fs=9)
box(ax,2.7,2.1,2.4,0.8,'Casos obrigatórios:\ntodos passam?',fs=9.5)
box(ax,2.7,0.7,2.4,0.8,'Demais casos:\nmédia não piora?',fs=9.5)
arrow(ax,2.0,1.95,2.7,2.5); arrow(ax,2.0,1.65,2.7,1.1)
box(ax,6.3,2.1,2.4,0.8,'Publica',fc=LTEAL,ec=TEAL,fs=11,bold=True,tc=TEAL)
box(ax,6.3,0.7,2.4,0.8,'Barra e investiga',fc=LOR,ec=ORANGE,fs=11,bold=True,tc=ORANGE)
arrow(ax,5.1,2.5,6.3,2.5,c=TEAL,text='sim, e sim',fs=8.5)
arrow(ax,5.1,1.1,6.3,1.1,c=ORANGE)
ax.text(5.7,0.45,'qualquer "não"',ha='center',fontsize=8.5,color=ORANGE)
ax.text(4.5,3.3,'Todo erro que chega a uma cliente vira caso novo',ha='center',fontsize=9,color=GRAY,style='italic')
save(fig,'f23_1.png')

# 24.1 trace
fig,ax=canvas(9,3.6)
spans=[('mensagem recebida',0,0.2,GRAY),('chamada ao modelo',0.25,1.6,ORANGE),('buscar_encomenda_anterior',1.9,0.7,TEAL),
       ('chamada ao modelo',2.7,1.3,ORANGE),('registrar_encomenda',4.1,0.6,TEAL),('chamada ao modelo',4.8,1.1,ORANGE),('resposta',6.0,0.2,GRAY)]
for i,(t,x0,w,c) in enumerate(spans):
    y=3.0-i*0.4
    ax.add_patch(FancyBboxPatch((0.4+x0,y),w,0.28,boxstyle='round,pad=0.01,rounding_size=0.05',fc=c,ec=c,alpha=0.85))
    ax.text(0.4+x0+w+0.08,y+0.14,t,va='center',fontsize=8.5,color=DARK)
ax.plot([0.4,7.0],[0.1,0.1],color=GRAY,lw=1)
ax.text(0.4,-0.15,'0 s',fontsize=8,color=GRAY); ax.text(6.7,-0.15,'6,4 s',fontsize=8,color=GRAY)
ax.text(0.4,3.45,'Um trace: a conversa inteira. Cada barra é um span, com tempo, dados e custo.',fontsize=9.5,color=TEAL,weight='bold')
save(fig,'f24_1.png')

# 25.1 trifeta
fig,ax=canvas(6,5)
for (x,y,c,t) in [(2.2,3.0,TEAL,'Dados\nprivados'),(3.8,3.0,ORANGE,'Conteúdo\nde fora'),(3.0,1.7,GRAY,'Canal\npara fora')]:
    ax.add_patch(Circle((x,y),1.25,fc=c,ec=c,alpha=0.18,lw=2))
    ax.text(x+(x-3)*0.55,y+(y-2.55)*0.55,t,ha='center',va='center',fontsize=10.5,color=c,weight='bold')
ax.text(3.0,2.6,'perigo',ha='center',va='center',fontsize=10,color=DARK,weight='bold')
ax.text(3.0,0.15,'Tire uma das três do mesmo agente',ha='center',fontsize=10,color=DARK)
save(fig,'f25_1.png')

# 28.1 lançamento
fig,ax=canvas(9,2.8)
fases=[('Modo sombra','agente escreve,\npessoa envia'),('Dúvidas simples','horário, cardápio'),('Encomendas','com confirmação'),('Pagamentos','com aprovação')]
for i,(t,s) in enumerate(fases):
    x=0.2+i*2.2
    box(ax,x,1.0,1.9,1.1,t+'\n'+s,fc=LTEAL if i else LG,ec=TEAL if i else GRAY,fs=9)
    if i: arrow(ax,x-0.3,1.55,x,1.55)
ax.text(4.5,2.4,'Avança quando os números ficam bons por tempo suficiente',ha='center',fontsize=10,color=TEAL,weight='bold')
ax.text(4.5,0.55,'mais autonomia →',ha='center',fontsize=9,color=GRAY)
save(fig,'f28_1.png')

# 30.1 arquitetura projeto final
fig,ax=canvas(9,4.6)
box(ax,0.2,3.5,1.8,0.7,'Mensagem\n+ sessão',fc=LG,ec=GRAY,fs=9.5)
box(ax,2.6,3.5,2.0,0.7,'conversar\n(controlador)',fs=9.5,bold=True)
box(ax,5.4,3.5,1.6,0.7,'modelo',fc=LOR,ec=ORANGE,fs=10)
arrow(ax,2.0,3.85,2.6,3.85); arrow(ax,4.6,3.95,5.4,3.95,c=ORANGE,text='pede',fs=8)
arrow(ax,5.4,3.7,4.6,3.7,c=ORANGE)
box(ax,2.6,1.9,2.0,0.95,'executar\n5 portões',fs=9.5,bold=True)
arrow(ax,3.6,3.5,3.6,2.85)
box(ax,5.4,1.9,3.3,0.95,'Sistema: agenda, encomendas,\nPix, estornos, aprovações',fs=9)
arrow(ax,4.6,2.37,5.4,2.37,c=TEAL)
box(ax,0.2,1.9,1.8,0.95,'Caderno\n(memória)',fs=9.5); arrow(ax,1.1,2.85,2.6,3.6,c=GRAY)
box(ax,5.4,0.5,1.6,0.8,'Pasta\n(RAG)',fs=9.5)
box(ax,2.6,0.5,2.0,0.8,'Trilha\n(trace)',fc=LG,ec=GRAY,fs=9.5)
arrow(ax,3.6,1.9,3.6,1.3,c=GRAY); arrow(ax,6.2,1.9,6.2,1.3,c=TEAL)
save(fig,'f30_1.png')
print('ok')
