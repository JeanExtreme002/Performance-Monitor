from PIL import Image
import pystray 

class TrayIcon(object):
    icon_fn = "icon.png"
    
    def __init__(self,name,title,*functions,icon=icon_fn):
        """
        Param *functions: Recebe sequências contendo ["texto do botão",função]
        Param icon: Recebe o nome do ícone a ser carregado.
        """

        items = []

        # Coloca os itens dentro do menu
        for function in functions:
            items.append(pystray.MenuItem(function[0],function[1]))
        menu = pystray.Menu(*items)

        # Carrega a imagem do ícone
        icon = Image.open(icon)

        # Cria o ícone
        self.__icon = pystray.Icon(name=name,title=title,icon=icon,menu=menu)


    def run(self):
        self.__icon.run()
    

    def stop(self):
        self.__icon.stop()


