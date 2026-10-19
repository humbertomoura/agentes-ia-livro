import json
class Item:
    def __init__(self, **kw): self.__dict__.update(kw)
class Resp:
    def __init__(self, output, text=""): self.output=output; self.output_text=text; self.status="completed"
class Responses:
    def __init__(self): self.n=0; self.log=[]
    def create(self, model, instructions, input, tools):
        self.log.append(len(input)); self.n+=1
        assert all(t["type"]=="function" for t in tools)
        if self.n==1:
            return Resp([Item(type="reasoning"),Item(type="function_call",name="consultar_agenda",arguments='{"dia":"sábado"}',call_id="c1"),
                         Item(type="function_call",name="consultar_preco",arguments='{"produto":"bolo de cenoura"}',call_id="c2")])
        if self.n==2:
            outs=[x for x in input if isinstance(x,dict) and x.get("type")=="function_call_output"]
            print("  [fake] outputs recebidos:", [(o["call_id"], o["output"]) for o in outs])
            return Resp([Item(type="function_call",name="consultar_agenda",arguments='{"dia":"sexta"}',call_id="c3")])
        outs=[x for x in input if isinstance(x,dict) and x.get("type")=="function_call_output"]
        print("  [fake] último output:", outs[-1])
        return Resp([Item(type="message")], "Sábado lotou, mas sexta tem vaga! Fica R$ 60,00.")
class OpenAI:
    def __init__(self): self.responses=Responses()
