from tkinter import Canvas,Label,Tk
import psutil
import src.util
import time

class MonitoringWindow(object):

    X = 30
    Y = 30

    VERTICAL = 1
    HORIZONTAL = 2

    cursor = "cross white"
    __movable = False
    __direction = HORIZONTAL

    def __init__(self,chromaKeyColor="black"):

        # Cria a janela realizando algumas configurações.
        self.__root = Tk()
        self.__root.resizable(False,False)
        self.__root.overrideredirect(True)
        self.__root["bg"] = chromaKeyColor
        self.__destroy = False

        # Define o tamanho da janela como sendo o tamanho do monitor do usuário.
        self.__width = self.__root.winfo_screenwidth()
        self.__height = self.__root.winfo_screenheight()
        self.__root.geometry("{}x{}+0+0".format(self.__width,self.__height))

        # Realiza o chroma key e configura a janela para ficar sempre no topo de tudo. 
        # Dessa forma, as informações ficarão sempre visíveis.
        self.__chromaKeyColor = chromaKeyColor
        self.__root.wm_attributes("-transparentcolor",self.__chromaKeyColor)
        self.__root.wm_attributes("-topmost", True)


    def adjustLocation(self):
        """
        Método para ajustar a posição dos textos na tela.
        """

        i = 0
        lastcoord = [0,0,0,0]

        for item in self.__items:
            if not item: continue
            coord = self.__canvas.bbox(item)
            
            # Se a direção for VERTICAL, o texto será posicionado em pilha, um em baixo do outro.
            if self.__direction == self.VERTICAL:
                self.__canvas.move(item,coord[0]*-1+self.X,coord[1]*-1+self.Y+self.__spacing*i)

            # Se a direção for HORIZONTAL, o texto será posicionado no lado dos outros textos.
            else:

                # Caso o item seja o primeiro texto, será adicionado à sua posição X a posição X do bloco de textos.
                if i == 0:
                    self.__canvas.move(item,coord[0]*-1+self.X,coord[1]*-1+self.Y)
                
                # Senão, a posição X do item será a posição X2 do último item somado ao tamanho da fonte.
                else:
                    self.__canvas.move(item,(coord[0]-lastcoord[2])*-1+self.__font[1],coord[1]*-1+self.Y)
                lastcoord = coord
            i+=1


    def build(self,color="red",font=("Arial",40),ping=True,cpu=True,ram=True,memory=True,battery=True,outline="black",direction=VERTICAL,movable=True):
        """
        Método para construir a parte gráfica 
        relacionada às informações de performance.
        """
    
        self.__ping = ping
        self.__cpu = cpu
        self.__ram = ram
        self.__memory = memory
        self.__battery = battery
        self.__color = color
        self.__font = font
        self.__outline = outline

        # Obtém a direção do texto
        if direction in [self.VERTICAL,self.HORIZONTAL]: self.__direction = direction
        
        # Cria um canvas que será usado para guardar os textos. 
        # Esse canvas possuirá uma cor do chroma key, para que 
        # ele suma e seja visível somente os textos.
        self.__canvas = Canvas(
            self.__root,
            bg=self.__chromaKeyColor,
            width=self.__width,
            height=self.__height,
            highlightthickness=0,
            )

        # Caso a opção "movable" seja True, o usuário poderá mover o texto caso ele clique no mesmo.
        if movable:
            self.__canvas.bind("<Button-1>",self.__move)
            self.__canvas.config(cursor=self.cursor)

        # Essa lista guardará o ID de todos os textos.
        self.__items = []

        # Cria um texto para informar o PING.
        if ping:
            self.__items.append(self.__canvas.create_text(0,0,text="PING:",fill=color,font=font,tag="PING"))

        # Cria um texto para cada CPU que o usuário possuir.
        if cpu:
            self.__items.append(self.__canvas.create_text(0,0,text="CPU:",fill=color,font=font,tag="CPU"))
            for i in range(psutil.cpu_count()):
                self.__items.append(self.__canvas.create_text(0,0,text="CPU {}:".format(i+1),fill=color,font=font,tag="CPU"))
        
        # Cria um texto para o uso de RAM.
        if ram:
            self.__items.append(self.__canvas.create_text(0,0,text="RAM:",fill=color,font=font,tag="RAM"))

        # Cria texto para mostrar o consumo de memória atual e a memória total.
        if memory:
            self.__items.append(self.__canvas.create_text(0,0,text="MEMORY:",fill=color,font=font,tag="MEMORY"))

        # Cria texto para informar a situação da bateria.
        if battery:
            self.__items.append(self.__canvas.create_text(0,0,text="BATTERY:",fill=color,font=font,tag="BATTERY"))


        # Obtém a altura dos textos para realizar um espaçamento entre eles.
        if len(self.__items) > 0:
            coord = self.__canvas.bbox(self.__items[0])
            self.__spacing = coord[3] - coord[1]

        # Atualiza a janela
        self.__update()
        self.__canvas.pack()


    def close(self):
        """
        Encerra totalmente a janela de monitoramento.
        """

        self.stop()
        self.__destroy = True


    def drawOutline(self):
        """
        Método para criar uma borda no texto.
        """
        
        size = 2
        color = self.__outline
        self.__canvas.delete('outline')
        
        # Percorre cada texto da lista.
        for item in self.__items:
            if not item: continue

            # Obtém as coordenadas do texto no formato (X,Y).
            coord = self.__canvas.bbox(item)
            coord = (coord[0]+((coord[2]-coord[0])//2) , coord[1]+((coord[3]-coord[1])//2))

            # Obtém o texto
            text = self.__canvas.itemcget(item,"text")

            # Desenha no canvas o mesmo texto com a mesma fonte, 
            # porém numa posição diferente para dar um efeito de borda.
            self.__canvas.create_text(coord[0]-size,coord[1],text=text,font=self.__font,fill=color,tag='outline')
            self.__canvas.create_text(coord[0]+size,coord[1],text=text,font=self.__font,fill=color,tag='outline')
            self.__canvas.create_text(coord[0],coord[1]-size,text=text,font=self.__font,fill=color,tag='outline')
            self.__canvas.create_text(coord[0],coord[1]+size,text=text,font=self.__font,fill=color,tag='outline')

            # Coloca o texto principal na frente.
            self.__canvas.tag_raise(item)
            

    def __drawRect(self):
        """
        Método para criar um retângulo caso o usuário tenha clicado no texto.
        """

        self.__canvas.delete("rect")

        # Verifica se o usuário clicou ou não no texto.
        if not self.__movable: return

        size = 4
        x1 = self.__width
        y1 = self.__height
        x2 = 0
        y2 = 0

        # Obtém as coordenadas (x1,y1,x2,y2) para desenhar o retângulo.
        for item in self.__items:
            coord = self.__canvas.bbox(item)
            if coord[0] < x1:
                x1 = coord[0]-10
            if coord[1] < y1:
                y1 = coord[1]-10
            if coord[2] > x2:
                x2 = coord[2]+10
            if coord[3] > y2:
                y2 = coord[3]+10

        # Cria um retângulo.
        self.__canvas.create_line((x1,y1),(x2,y1),(x2,y2),(x1,y2),(x1,y1),fill=self.__color,width=size,tag="rect")
        x1 -= size//2
        y1 -= size//2
        x2 += size//2
        y2 += size//2

        # Cria uma borda externa.
        self.__canvas.create_line((x1,y1),(x2,y1),(x2,y2),(x1,y2),(x1,y1),fill=self.__outline,tag="rect")
        x1 += size
        y1 += size
        x2 -= size
        y2 -= size

        # Cria uma borda interna.
        self.__canvas.create_line((x1,y1),(x2,y1),(x2,y2),(x1,y2),(x1,y1),fill=self.__outline,tag="rect")

    
    def __move(self,event=None):
        """
        Método para mover o texto para a posição X,Y do mouse.
        """

        # Deleta retângulo do mouse.
        self.__canvas.delete("mouse")

        # Caso o método tenha sido chamado por causa de um método, o texto não será movimentado.
        if event:
            if not self.__canvas.focus_get() and not self.__movable: return
            self.__movable = not self.__movable
            return

        if not self.__movable: return

        # Obtém a posição X,Y do mouse.
        x = self.__root.winfo_pointerx()
        y = self.__root.winfo_pointery()
        
        # Verifica se o mouse está parado. Se sim será retornado False. Se não será retornado True.
        if self.X == x and self.Y == y: return False

        # Cria um retângulo para que o usuário possa clicar num item do canvas fazendo
        # com que o mesmo tenha foco. Dessa forma, o usuário poderá sair da opção de mover o texto.
        size = 5
        self.__canvas.create_rectangle(x-size-3,y-size-3,x+size-3,y+size-3,fill=self.__color,outline=self.__outline,tag="mouse")
        self.X = x+3
        self.Y = y+3
        return True


    def run(self,updateIn=1000,number_size_after_floating_point=2):
        """
        Método para inicializar o monitoramento.
        """

        self.__stop = False
        i = 1
        ping = "0"
        total_cpu_usage = 0
        memory_percent = 0
        memory_used = 0
        memory_total = 0
        battery_percent = 0
        battery_power_plugged = False

        # Atualiza as informações enquanto o usuário não 
        # pedir para parar o monitoramento.

        while not self.__stop:
            
            # Se tiver passado X ou mais segundos, as informações dos textos serão atualizadas

            if not self.__movable:

                # Obtém o ping.
                if self.__ping:
                    c_ping = src.util.getLatency()
                    if not c_ping: c_ping = "Undefined"

                # Obtém o consumo de CPU.
                if self.__cpu:
                    cpu = psutil.cpu_percent(0,True)
                    c_total_cpu_usage = sum(cpu)*(100/(len(cpu)*100))
                    cpu_i = -1

                # Obtém o consumo de memória RAM.
                if self.__ram or self.__memory:
                    memory = psutil.virtual_memory()

                # Obtém as informações de bateria.
                if self.__battery:
                    battery = psutil.sensors_battery()
        
                # Atualiza as informações de cada item.
                for item in self.__items:
                    if not item: continue
                    
                    # Obtém a tag do item e atualiza a informação.
                    tag = self.__canvas.itemcget(item,"tag")

                    # Antes de fazer a atualização de um determinado texto, será verificado 
                    # se os novos dados são iguais aos dados que estão no texto. Essa verificação serve
                    # para que não haja um consumo desnecessário de processamento. Dessa forma, será atualizado
                    # o texto apenas se for necessário.

                    # Atualiza o PING.
                    if tag.lower() == "ping":
                        if ping == c_ping: continue
                        text = "PING: "+c_ping
                        ping = c_ping

                    # Atualiza as informações de consumo de CPU.
                    elif tag.lower() == "cpu":
                        if total_cpu_usage == c_total_cpu_usage:
                            continue
                        
                        if cpu_i == -1:
                            text = "CPU: %.{}f%%".format(number_size_after_floating_point)%c_total_cpu_usage
                        else:
                            text = "CPU %i: %.{}f%%".format(number_size_after_floating_point)%(cpu_i+1,cpu[cpu_i])

                        cpu_i += 1
                        if cpu_i == len(cpu):
                            total_cpu_usage = c_total_cpu_usage

                    # Atualiza as informações de consumo de RAM.
                    elif tag.lower() == "ram":
                        if memory_percent == memory.percent:
                            continue

                        text = "RAM: %.{}f%%".format(number_size_after_floating_point)%memory.percent
                        memory_percent = memory.percent

                    # Atualiza as informações de consumo da memória.
                    elif tag.lower() == "memory":
                        if memory_used == memory.used and memory_total == memory.total:
                            continue

                        text = "MEMORY: %i %s / %i %s"%(*src.util.getFormattedSize(memory.used),*src.util.getFormattedSize(memory.total))
                        memory_used = memory.used
                        memory_total = memory.total

                    # Atualiza as informações de bateria.
                    elif tag.lower() == "battery":
                        if battery_percent == battery.percent and battery_power_plugged == battery.power_plugged:
                            continue

                        text = "BATTERY: %i %%  "%battery.percent
                        if battery.power_plugged:
                            text += "( ON )"
                        else:
                            text += "( OFF )"
                        battery_percent = battery.percent
                        battery_power_plugged = battery.power_plugged

                    else:
                        continue

                    # Atualiza o texto.
                    self.__canvas.delete("outline")
                    self.__canvas.itemconfig(item,text=text) 

                    # Como os textos na posição horizontal podem ficar desorganizados facilmente 
                    # devido às mudanças de tamanho, a janela será atualizada a cada texto atualizado. 
                    if self.__direction == self.HORIZONTAL: self.__update()

                # Atualiza a janela.
                self.__update()
                time.sleep(updateIn/1000)

            else:

                # Atualiza se o mouse estiver numa posição diferente do texto ou a variável "movable" for False
                if self.__move() or not self.__movable:
                    self.__update()
                time.sleep(0.01)

        # Destrói a GUI caso o método close() seja chamado.
        if self.__destroy:
            self.__root.destroy()


    def stop(self):
        """
        Método para parar o monitoramento.
        Este metódo apenas interrompe a atualização de 
        informação do método run(), mas ele não destrói a GUI.
        """
        self.__stop = True


    def __update(self):
        """
        Método para atualizar os textos.
        """

        # Ajusta a posição dos textos na tela e espera um tempo para 
        # não consumir muito processamento do usuário.
        self.adjustLocation()

        # Desenha uma borda no texto.
        self.drawOutline()   

        # Desenha um retângulo caso o usuário tenha clicado nos textos.
        self.__drawRect()

        # Atualiza a tela.
        self.__root.update()

