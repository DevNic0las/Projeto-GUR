import sys
import os
from database.init_database import initdatabase



def verifiy_path():
    print(sys.path)
    initdatabase()
if __name__ == "__main__":
    verifiy_path()