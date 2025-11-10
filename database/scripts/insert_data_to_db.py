from database.init_database import initdatabase
def insert_data_hospitals(hospitals):
    
    hospitals_col = initdatabase()
    hospitals_col.insert_many(hospitals)

def insert_data_deases(diseases):
    diseases_col = initdatabase()
    diseases_col.insert_many(diseases)
    
if __name__ == "__main__":
    
     """ 
    dic = [
    {"name": "Hospital da Restauração (HR) - Derby (Grande Trauma)", "type": "Hospital", "diseases":[
        {diseases_id[]}
    ]},
    {"name": "Hospital Getúlio Vargas (HGV) - Cordeiro", "type": "Hospital", "diseases":[
        {diseases_id[]}
    ]},
    {"name": "Hospital Agamenon Magalhães (HAM) - Casa Amarela", "type": "Hospital", "diseases":[
        {diseases_id[]}
    ]},
    {"name": "Hospital Barão de Lucena (HBL) - Iputinga", "type": "Hospital", "diseases":[
        {diseases_id[]}
    ]},
    {"name": "Hospital Oswaldo Cruz (HUOC) - Santo Amaro", "type": "Hospital", "diseases":[
        {diseases_id[]}
    ]},
    {"name": "PROCAPE - Pronto Socorro Cardiológico de Pernambuco", "type": "Hospital", "diseases":[
        {diseases_id[]}
    ]},
    
    
    {"name": "Hospital da Mulher do Recife (HMR) - Curado (Ginecológica/Obstétrica)", "type": "Hospital"},
    {"name": "Hospital Pediátrico Helena Moura - Tamarineira (Pediátrica)", "type": "Hospital"},
    {"name": "Hospital das Clínicas (HC/UFPE) - Cidade Universitária", "type": "Hospital"},
    {"name": "IMIP - Instituto de Medicina Integral Prof. Fernando Figueira", "type": "Hospital"},

   
    {"name": "UPA Caxangá (Prof. Dr. Fernando Figueira)", "type": "UPA"},
    {"name": "UPA Torrões (Prof. Dr. Etevaldo de Luna)", "type": "UPA"},
    {"name": "UPA Ibura (Maria Esther Souto Carvalho)", "type": "UPA"},
    {"name": "UPA Imbiribeira (Maria de Lourdes M. de Souza)", "type": "UPA"},
    {"name": "UPA Nova Descoberta (Abdias de Barros Correia)", "type": "UPA"},
    {"name": "UPA Boa Viagem (Jurema Paes Barreto)", "type": "UPA"},
    {"name": "UPA Olinda", "type": "UPA"},

    
    {"name": "UPAE Arruda", "type": "UPAE"},
    {"name": "UPAE Ibura", "type": "UPAE"},
    {"name": "UPAE Especialidades Mustardinha", "type": "UPAE"},

   
    {"name": "Policlínica Gouveia de Barros - Pina", "type": "Policlínica"},
    {"name": "Policlínica Lessa de Andrade - Madalena", "type": "Policlínica"},
    {"name": "Policlínica Arnaldo Marques - Ibura", "type": "Policlínica"},
    {"name": "Policlínica Clementino Fraga - Vasco da Gama", "type": "Policlínica"},
    {"name": "Policlínica Albert Sabin - Tamarineira", "type": "Policlínica"},
    {"name": "Policlínica Waldemar de Oliveira - Santo Amaro", "type": "Policlínica"},
    {"name": "Policlínica Salomão Kelner - Água Fria", "type": "Policlínica"},

 
    {"name": "CAPS Espaço Azul (Infanto-Juvenil)", "type": "CAPS"},
    {"name": "CAPS Casa Forte", "type": "CAPS"},
    {"name": "CAPS Gouveia de Barros", "type": "CAPS"},
    {"name": "CAPS Adauto Botelho", "type": "CAPS"},
    {"name": "CAPS Cabo de Santo Agostinho", "type": "CAPS"},

   
    {"name": "Centro de Saúde Bidu Krause", "type": "Centro"},
    {"name": "Centro de Especialidades Odontológicas (CEO)", "type": "Centro"},
    {"name": "Centro de Testagem e Aconselhamento (CTA)", "type": "Centro"}
    ] 
    """
    # insert_data_hospitals(dic)

dic_diseases = [
     {}
    ]
insert_data_deases(dic_diseases)
    
    