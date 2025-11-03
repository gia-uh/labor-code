import os
import json
from pathlib import Path
import pandas as pd
    
CAT = {
    "additions":"Agregar" ,
    "deletions":"Eliminar",
    "modifications":"Modificar",
    "questions": "Dudas"
}    
    
def load_all_data_from_folder(file_option: str ="all", cat_option: str ="all"):
    """
    Loads all JSON data from the specified folders
    """
    data = []

    cat_option = "all"

    folders = [os.path.join("data", f) for f in os.listdir("data")]

    for folder in folders:
        for file in Path(folder).iterdir():
            try:
                content = json.load(file.open())
                for key,value in content.items():
                    if key.isnumeric():
                        base = {"Paragrafo": key, "Area":content["Area"]}
                        if cat_option == "all":
                            for k,v in value.items():
                                new_base = base.copy()
                                new_base["Categoria"] = CAT[k]
                                for text in v:
                                    new = new_base.copy()
                                    new["Informacion"] = text.strip()
                                    data.append(new)
                        else:
                            base.update({"Categoria": CAT[cat_option]})
                            for text in value[cat_option]:
                                new = base.copy()
                                new["Informacion"] = text.strip()
                                data.append(new)
                            
            
            except Exception as e:
                print(f"Error al cargar {file}: {str(e)}")
    
    return data





print( pd.DataFrame(load_all_data_from_folder()))