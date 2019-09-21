from monitoringWindow import MonitoringWindow
from trayIcon import TrayIcon
from threading import Thread
from tkinter import Entry,Frame,IntVar,Label,Tk,Checkbutton
from tkinter import ttk
import json
import sys
import os

class App(object):

    bigText_color = "red"
    bigText_font = ("Arial",30)

    button_width = 10
    button_font = ("Arial",18)

    chromaKeyColors = ["gray2","gray3"]

    default_settings = {
        "Text":{
            "SIZE":25,
            "COLOR":"yellow",
            "FONT":"Arial Black"
        },
        "Show":{
            "PING":1,
            "CPU":1,
            "RAM":1,
            "MEMORY":0,
            "BATTERY":0
        },
        "System":{
            "DIRECTION":1,
            "MOVABLE":1,
            "NUMBER SIZE AFTER FLOATING POINT":1,
            "UPDATE":500
        }
    }

    icon_fn = "images/icon.ico"

    settings_file = "settings/settings.json"

    text_color = "black"
    text_font = ("Arial",13)

    w_color = "gray90"
    w_geometry = (400,280)
    w_title = "Performance Monitor"

    __number_size_after_floating_point = None
    __update = None


    def run(self):
        """
        Método para iniciar o programa.
        """

        # Cria uma janela e realiza algumas configurações.
        self.__root = Tk()
        self.__root["bg"] = self.w_color
        self.__root.geometry("{}x{}".format(*self.w_geometry)) 
        self.__root.title(self.w_title)
        self.__root.resizable(False,False)
        self.__root.iconbitmap(self.icon_fn)

        # Obtém as configurações da última sessão. 
        # Caso não seja possível, as configurações serão as padrões.
        settings = self.loadSettings()
        if not settings: settings = self.default_settings 

        # Define configurações internas do sistema
        self.__update = int(settings["System"]["UPDATE"])
        self.__number_size_after_floating_point = int(settings["System"]["NUMBER SIZE AFTER FLOATING POINT"])

        # Cria o título
        Label(self.__root,bg=self.w_color,fg=self.bigText_color,font=self.bigText_font,text="Settings").pack(pady=20)

        # Cria frame para inserir os widgets relacionados à configuração do texto.
        self.__textConfigFrame = Frame(self.__root,bg=self.w_color)
        self.__textConfigFrame.pack(pady=5)

        # Cria título para informar onde será aplicada determinada configuração.
        Label(
            self.__textConfigFrame,
            font=self.text_font,
            fg=self.text_color,
            bg=self.w_color,
            text="Size: "
            ).pack(side="left")

        # Cria uma entry para inserir o tamanho do texto.
        self.__sizeEntry = Entry(self.__textConfigFrame,font=self.text_font,width=self.text_font[1]//3)
        self.__sizeEntry.insert(0,str(settings["Text"]["SIZE"]))
        self.__sizeEntry.pack(side="left")

        # Cria um espaço entre os widgets.
        Label(self.__textConfigFrame,bg=self.w_color,width=2).pack(side="left")

        # Cria título para informar onde será aplicada determinada configuração.
        Label(
            self.__textConfigFrame,
            font=self.text_font,
            fg=self.text_color,
            bg=self.w_color,
            text="Color: "
            ).pack(side="left")

        # Cria uma entry para inserir a cor do texto.
        self.__colorEntry = Entry(self.__textConfigFrame,font=self.text_font,width=int(self.text_font[1]/2))
        self.__colorEntry.insert(0,settings["Text"]["COLOR"])
        self.__colorEntry.pack(side="left")

        # Cria um espaço entre os widgets
        Label(self.__textConfigFrame,bg=self.w_color,width=2).pack(side="left")

        # Cria título para informar onde será aplicada determinada configuração.
        Label(
            self.__textConfigFrame,
            font=self.text_font,
            fg=self.text_color,
            bg=self.w_color,
            text="Font: "
            ).pack(side="left")

        # Cria uma entry para inserir a fonte do texto.
        self.__fontEntry = Entry(self.__textConfigFrame,font=self.text_font,width=int(self.text_font[1]/1.5))
        self.__fontEntry.insert(0,settings["Text"]["FONT"])
        self.__fontEntry.pack(side="left")

        # Cria frame para inserir os widgets relacionados à posição do texto na tela
        self.__textPositionFrame = Frame(self.__root,bg=self.w_color)
        self.__textPositionFrame.pack(pady=5)


        # Cria título para informar onde será aplicada determinada configuração.
        Label(
            self.__textPositionFrame,
            font=self.text_font,
            fg=self.text_color,
            bg=self.w_color,
            text="Position: "
            ).pack(side="left")    

        def changeDirection(direction):
            """
            Função para desmarcar um checkbutton de direção.
            """
            if direction:
                self.__verticalCB.var.set(0)
            else:
                self.__horizontalCB.var.set(0)

        # Obtém a direção do texto padrão.
        if int(settings["System"]["DIRECTION"]):
            direction = [1,0]
        else:
            direction = [0,1]

        # Cria um checkbutton para a direção do texto ser vertical.
        self.__verticalCB = Checkbutton(self.__textPositionFrame,bg=self.w_color,text="Vertical",command=lambda:changeDirection(0))
        self.__verticalCB.var = IntVar()
        self.__verticalCB.var.set(direction[0])
        self.__verticalCB.config(variable=self.__verticalCB.var)
        self.__verticalCB.pack(side="left")

        # Cria um checkbutton para a direção do texto ser horizontal.
        self.__horizontalCB = Checkbutton(self.__textPositionFrame,bg=self.w_color,text="Horizontal",command=lambda:changeDirection(1))
        self.__horizontalCB.var = IntVar()
        self.__horizontalCB.var.set(direction[1])
        self.__horizontalCB.config(variable=self.__horizontalCB.var)
        self.__horizontalCB.pack(side="left")

        # Cria um checkbutton para habilitar ou não a opção de mover o texto ao clicar nele.
        self.__movableCB = Checkbutton(self.__textPositionFrame,bg=self.w_color,text="Movable")
        self.__movableCB.var = IntVar()
        self.__movableCB.var.set(int(settings["System"]["MOVABLE"]))
        self.__movableCB.config(variable=self.__movableCB.var)
        self.__movableCB.pack(side="left")

        Label(self.__textPositionFrame,bg=self.w_color,width=9).pack(side="left")


        # Cria frame para inserir os widgets relacionados à configuração do que o usuário deseja ou não ver.
        self.__selectionFrame = Frame(self.__root,bg=self.w_color)
        self.__selectionFrame.pack(pady=5)

        # Cria título para informar onde será aplicada determinada configuração.
        Label(
            self.__selectionFrame,
            font=self.text_font,
            fg=self.text_color,
            bg=self.w_color,
            text="Show: "
            ).pack(side="left")

        # Cria um checkbutton para habilitar ou não a opção de ver o PING.
        self.__pingCB = Checkbutton(self.__selectionFrame,bg=self.w_color,text="PING")
        self.__pingCB.var = IntVar()
        self.__pingCB.var.set(int(settings["Show"]["PING"]))
        self.__pingCB.config(variable=self.__pingCB.var)
        self.__pingCB.pack(side="left")

        # Cria um checkbutton para habilitar ou não a opção de ver o uso da CPU.
        self.__cpuCB = Checkbutton(self.__selectionFrame,bg=self.w_color,text="CPU")
        self.__cpuCB.var = IntVar()
        self.__cpuCB.var.set(int(settings["Show"]["CPU"]))
        self.__cpuCB.config(variable=self.__cpuCB.var)
        self.__cpuCB.pack(side="left")

        # Cria um checkbutton para habilitar ou não a opção de ver o uso da memória RAM.
        self.__ramCB = Checkbutton(self.__selectionFrame,bg=self.w_color,text="RAM")
        self.__ramCB.var = IntVar()
        self.__ramCB.var.set(int(settings["Show"]["RAM"]))
        self.__ramCB.config(variable=self.__ramCB.var)
        self.__ramCB.pack(side="left")

        # Cria um checkbutton para habilitar ou não a opção de ver a quantidade de memória em uso e total.
        self.__memoryCB = Checkbutton(self.__selectionFrame,bg=self.w_color,text="Memory")
        self.__memoryCB.var = IntVar()
        self.__memoryCB.var.set(int(settings["Show"]["MEMORY"]))
        self.__memoryCB.config(variable=self.__memoryCB.var)
        self.__memoryCB.pack(side="left")        

        # Cria um checkbutton para habilitar ou não a opção de ver a quantidade de bateria.
        self.__batteryCB = Checkbutton(self.__selectionFrame,bg=self.w_color,text="Battery")
        self.__batteryCB.var = IntVar()
        self.__batteryCB.var.set(int(settings["Show"]["BATTERY"]))
        self.__batteryCB.config(variable=self.__batteryCB.var)
        self.__batteryCB.pack(side="left")  

        Label(self.__selectionFrame,bg=self.w_color,width=1).pack(side="left")

        # Cria estilo para o botão.
        style = ttk.Style()
        style.configure(
            "TButton",
            background=self.w_color,
            font=self.button_font,
            width=self.button_width
            )
        ttk.Button()

        # Cria um botão para iniciar o monitoramento.
        self.__button = ttk.Button(self.__root,style="TButton",text="Start",command=self.__start)
        self.__button.pack(pady=15)
        self.__root.mainloop()


    def loadSettings(self):
        """
        Método para carregar as configurações do programa.
        """

        # Caso o diretório do arquivo não exista, o mesmo será criado.
        if not os.path.exists(os.path.dirname(self.settings_file)):
            os.mkdir(os.path.dirname(self.settings_file))
        
        # Retorna caso não o arquivo não exista.
        if not os.path.exists(self.settings_file): return

        # Carrega o arquivo e retorna um dicionário.
        file = open(self.settings_file)
        settings = file.read()
        file.close()
        return json.loads(settings)


    def saveSettings(self,size,color,font,ping,cpu,ram,memory,battery,*system):
        """
        Método para salvar as configurações do programa.
        """

        file = open(self.settings_file,"w")
        settings = {}
        settings["Text"] = {}
        settings["Text"]["SIZE"] = size
        settings["Text"]["COLOR"] = color
        settings["Text"]["FONT"] = font
        settings["Show"] = {}
        settings["Show"]["PING"] = bool(ping)
        settings["Show"]["CPU"] = bool(cpu)
        settings["Show"]["RAM"] = bool(ram)
        settings["Show"]["MEMORY"] = bool(memory)
        settings["Show"]["BATTERY"] = bool(battery)
        settings["System"] = {}
        settings["System"]["DIRECTION"] = bool(system[0])
        settings["System"]["MOVABLE"] = bool(system[1])
        settings["System"]["NUMBER SIZE AFTER FLOATING POINT"] = int(system[2])
        settings["System"]["UPDATE"] = int(system[3])
        file.write(json.dumps(settings,indent=2))
        file.close()


    def __start(self):
        """
        Método para inciar o monitoramento.
        """

        # Obtém o tamanho do texto.
        try:
            size = int(self.__sizeEntry.get())
        except:
            size = self.default_settings["Text"]["SIZE"]
        
        # Obtém a cor do texto.
        color = self.__colorEntry.get()

        # Obtém a cor utilizada para fazer chroma key.
        if color == self.chromaKeyColors[0]: chromaKeyColor = self.chromaKeyColors[1]
        else: chromaKeyColor = self.chromaKeyColors[0]

        # Salva as configurações desta sessão.
        self.saveSettings(
            size,
            color,
            self.__fontEntry.get(),
            self.__pingCB.var.get(),
            self.__cpuCB.var.get(),
            self.__ramCB.var.get(),
            self.__memoryCB.var.get(),
            self.__batteryCB.var.get(),
            self.__verticalCB.var.get(),
            self.__movableCB.var.get(),
            self.__number_size_after_floating_point,
            self.__update
        )

        # Coloca a font e o tamanho juntos numa tupla para ser usado nos widgets.
        font = (self.__fontEntry.get(),size)

        # Destrói a janela inicial do programa.
        self.__root.destroy()

        # Cria uma janela para realizar o monitoramento.
        monitor = MonitoringWindow(chromaKeyColor)

        # Define a direção do texto.
        if self.__horizontalCB.var.get():
            direction = monitor.HORIZONTAL
        else:
            direction = monitor.VERTICAL

        # Constrói a parte gráfica.
        monitor.build(
            color,
            font,
            self.__pingCB.var.get(),
            self.__cpuCB.var.get(),
            self.__ramCB.var.get(),
            self.__memoryCB.var.get(),
            self.__batteryCB.var.get(),
            outline="black",
            direction=direction,
            movable=self.__movableCB.var.get()
            )
        

        def close(systray):
            """
            Função para fechar o programa
            """
            monitor.close()

        # Cria um ícone de bandeja.
        trayIcon = TrayIcon(
            self.w_title,
            on_quit=close,
            icon=self.icon_fn
            )
        
        # Inicializa o ícone de bandeja.
        trayIcon.run()

        # Inicia o monitoramento.
        monitor.run(self.__update,self.__number_size_after_floating_point)

if __name__ == "__main__" and "win" in sys.platform:
    App().run()
