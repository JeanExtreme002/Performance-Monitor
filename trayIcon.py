from infi.systray import SysTrayIcon 

class TrayIcon(object):
    icon_fn = "icon.png"
    
    def __init__(self,title,menu=None,on_quit=None,icon=icon_fn):
        """
        Param *menu: Recebe tupla contendo tuplas com ("texto do botão","ícone do menu",função).
        Param icon: Recebe o nome do ícone a ser carregado.
        """

        self.__sysTrayIcon = SysTrayIcon(icon,title,menu,on_quit=on_quit)

    def run(self):
        self.__sysTrayIcon.start()
    

    def stop(self):
        self.__sysTrayIcon.shutdown()


