Modelo Usado: Gemini Hydrogen Medium pelo CLI do Antigravity
A ferramenta foi usado unica e exclusivamente para criação e validação dos testes finais, explicando o porque de um teste especifico não rodar, e assegurando que o resultado final foi totalmente consistente com o esperado. Nenhum código relacionado ao CLI foi gerado por meio de IA

Além disso, o gemini nativo do google foi utilizado como meio de pesquisa para buscar como inverter a ordem de uma lista gerada pela função "sorted()", utilizado em:
     "ranked_hotels = sorted(data_by_hotel.items(), key=lambda item: (-item[1]["amount"], item[0]))"