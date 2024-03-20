from bplustree import Bplustree
from utils import print_tree


tree = Bplustree(4)
def menu ():
    print("insert -------> 1")
    print("delete -------> 2")
    print("insert -------> 3")
    print("insert -------> 4")



while (True):
    menu()
    choix=int(input("Entrer votre choix "))
    
    match choix :
        case 1:
            value=int(input("entere la valeur a ajouter"))
            tree.insert(value)
            print("\n")
        case 2:
            value=int(input("entere la valeur a supprimer"))
            tree.delete(value)
            print("\n")

        case 3:
            print_tree(tree.root, '   ', 0)

        case 4:
            break
        case default :
            print("invalide choice")
