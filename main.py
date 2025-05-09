import pygame as pg
import ctypes as ct
import math as m
#import timeit (commented out functions were used for testing)

pg.init()

zoom: int = 50
origin: list[int] = [0, 0]
anchor: tuple[int] = (0, 0)
anchorTo: tuple[int] = (0, 0)
rightMouseHeld: bool = False
leftMouseHeld: bool = False
isPaused: bool = False
isDarkMode: bool = True
isInPlayMode: bool = False
testedScreenSize: dict[int] = {
    "height": 0,
    "width": 0,
    "zoom": zoom
}

BLACK: tuple[int] = (0, 0, 0)
GRAY: tuple[int] = (127, 127, 127)
WHITE: tuple[int] = (255, 255, 255)
display = pg.display.set_mode((1600,837), pg.RESIZABLE)
pg.display.set_caption("Conway's Game of Life")
window = pg.display.get_wm_info()["window"]
ct.windll.user32.ShowWindow(window, 3)
pg.display.flip()

#UI Classes:
class UIWrapper:
    def __init__(self):
        self.UIElements: dict[dict[list]] = {
            "layer0":{
                "button": [],
                "rect": [],
                "text": []
            },
            "layer1":{
                "button": [],
                "rect": [],
                "text": []
            },
            "layer2":{
                "button": [],
                "rect": [],
                "text": []
            },
        }

    def getAttribute(self, element, attribute):
        try:
            return element.__dict__[attribute]
        except:
            return element[attribute]

    def addButton(self, x: float, y: float, width: float, height: float, text: str, fontType: str, fontSizepct: float, textColor: tuple[int], color: tuple[int], hoverColor: tuple[int], displayFlag: bool, interactableWhilePaused: bool, layer: int, action = None):
        self.UIElements[f"layer{layer}"]["button"].append(Button(layer, x, y, width, height, text, fontType, fontSizepct, textColor, color, hoverColor, displayFlag, interactableWhilePaused, action))
        return self.UIElements[f"layer{layer}"]["button"][-1]

    def addRect(self, xpct: float, ypct: float, widthpct: float, heightpct: float, color: tuple[int], displayFlag: bool, layer: int):
        self.UIElements[f"layer{layer}"]["rect"].append({"layer": layer, "color": color, "xpct": xpct, "ypct": ypct, "widthpct": widthpct, "heightpct": heightpct, "displayFlag": displayFlag})
        return self.UIElements[f"layer{layer}"]["rect"][-1]

    def addText(self, text: str, textColor: tuple[int], xpct: float, ypct: float, fontType: str, fontSizepct: float, displayFlag: bool, layer: int):
        self.UIElements[f"layer{layer}"]["text"].append({"layer": layer, "text": text, "textColor": textColor, "xpct": xpct, "ypct": ypct, "fontType": fontType, "fontSizepct": fontSizepct, "fontSize": int(fontSizepct), "displayFlag": displayFlag})
        return self.UIElements[f"layer{layer}"]["text"][-1]

    def setElementVisibility(self, elements: list, displayFlag):
        for layer in range(3):
            for element in elements:
                if self.getAttribute(element, "layer") != layer:
                    continue
                try:
                    element.displayFlag = displayFlag
                except:
                    element["displayFlag"] = displayFlag


    def drawElements(self):
        for layer in range(3):
            for element in self.UIElements[f"layer{layer}"]["rect"]: 
                    if element["displayFlag"]:
                        if layer == 1:
                            s = pg.Surface(display.get_size(), pg.SRCALPHA)
                            s.set_alpha(element["color"][3])
                            s.fill((element["color"][0], element["color"][1], element["color"][2]))
                            display.blit(s, (0, 0))
                            continue
                        element["rect"] = pg.Rect(int(display.get_width() * element["xpct"] / 100), int(display.get_height() * element["ypct"] / 100), int(display.get_width() * element["widthpct"] / 100), int(display.get_height() * element["heightpct"] / 100))
                        pg.draw.rect(display, element["color"], element["rect"])
            for element in self.UIElements[f"layer{layer}"]["text"]: 
                 if element["displayFlag"]:
                     element["fontSize"] = int(min(display.get_width(), display.get_height()) * element["fontSizepct"] / 100)
                     font = pg.font.Font(element["fontType"], element["fontSize"])
                     textSurface = font.render(element["text"], True, element["textColor"])
                     rect = pg.Rect(0, 0, textSurface.get_width(), textSurface.get_height())
                     rect.centerx = int(display.get_width() * element["xpct"] / 100)
                     rect.top =  int(display.get_height() * element["ypct"] / 100)
                     display.blit(textSurface, rect)
            for element in self.UIElements[f"layer{layer}"]["button"]:
                if element.displayFlag:
                    if (not leftMouseHeld) and (not (element.interactableWhilePaused ^ isPaused)):
                        element.Hover()
                    element.Draw()

class Button:
    def __init__(self, layer: int, x: float, y: float, width: float, height: float, text: str, fontType: str, fontSizepct: float, textColor: tuple[int], color: tuple[int], hoverColor: tuple[int], displayFlag: bool, interactableWhilePaused: bool, action = None):
        self.layer = layer
        self.xpct: float = x
        self.ypct: float = y
        self.widthpct: float = width
        self.heightpct: float = height
        self.rect = pg.Rect(int(display.get_width() * x / 100), int(display.get_height() * y / 100), int(display.get_width() * width / 100), int(display.get_height() * height / 100))
        self.text: str = text
        self.fontSizepct: int = fontSizepct
        self.fontSize: int = int(min(display.get_width(), display.get_height()) * self.fontSizepct / 100)
        self.fontType: str = fontType
        self.font = pg.font.Font(self.fontType, self.fontSize)
        self.textColor: tuple[int] = textColor
        self.color: tuple[int] = color
        self.initialColor: tuple[int] = color
        self.hoverColor: tuple[int] = hoverColor
        self.displayFlag: bool = displayFlag
        self.interactableWhilePaused: bool = interactableWhilePaused
        self.action: None = action

    def UpdateDimensions(self):
        self.rect = pg.Rect(int(display.get_width() * self.xpct / 100), int(display.get_height() *  self.ypct / 100), int(display.get_width() *  self.widthpct / 100), int(display.get_height() * self.heightpct / 100))
        self.fontSize: int = int(min(display.get_width(), display.get_height()) * (self.fontSizepct / 100))
        self.font = pg.font.Font(self.fontType, self.fontSize)

    def Draw(self):
        self.UpdateDimensions()
        pg.draw.rect(display, self.color, self.rect)
        textSurface = self.font.render(self.text, True, self.textColor)
        textRect = textSurface.get_rect(center = self.rect.center)
        display.blit(textSurface, textRect)

    def HandleInteraction(self):
        self.color = self.initialColor
        if self.action:
             self.action()
    
    def Hover(self):
        if self.rect.collidepoint(pg.mouse.get_pos()):
            self.color = self.hoverColor
        else:
            self.color = self.initialColor
#(used to be in a class)
def addCell(cellPos: tuple[int], isLive: bool):
    cells[cellPos] = [isLive,0]

def removeCell(cellPos: tuple[int]):
    cells.pop(cellPos, 0)

def getImportantCells():
    tempDict = cells.copy()
    for cell in tempDict: 
        surroundingCells: list = [(cell[0] - 1, cell[1] + 1), (cell[0], cell[1] + 1), (cell[0] + 1, cell[1] + 1),
                                 (cell[0] - 1, cell[1]), (cell[0] + 1, cell[1]),
                                 (cell[0] - 1, cell[1] - 1), (cell[0], cell[1] - 1), (cell[0] + 1, cell[1] - 1)
                                 ]
        for cellPos in surroundingCells:
            if cellPos in tempDict:
                cells[cell][1] += 1
            else:
                cells.setdefault(cellPos, [False, 0])
                cells[cellPos][1] += 1

def applyRules():
    global cells
    tempDict = {}
    for cellPos, cell in cells.items():
        if (cell[1] == 3 or (cell[1] == 2 and cell[0])):
            tempDict[cellPos] = [True, 0]
    cells = tempDict.copy()

def advanceGeneration():
    getImportantCells()
    applyRules()
#end of "class"

#Helper Class:
class convert:
    class centerbased:
        def x(x: int) -> int:
            return centerx + x
        def y(y: int) -> int:
            return centery - y
    class cornerbased:
        def x(x: int) -> int:
            return x - centerx
        def y(y: int) -> int:
            return centery - y
    class cellPos:
        def x(x: int) -> int:
            return convert.centerbased.x(x * zoom - m.ceil(zoom / 2)) + 1 - origin[0]
        def y(y: int) -> int:
            return convert.centerbased.y(y * zoom + m.ceil(zoom / 2)) + 1 + origin[1]
    class realPos:
        def x(x: int) -> int:
            return convert.cornerbased.x(x + origin[0] + zoom / 2) // zoom
        def y(y: int) -> int:
            return convert.cornerbased.y(y - origin[1] - zoom / 2) // zoom

#Helper Functions
def isOnScreen(centerBasedPos: tuple[int], margin: int) -> bool:
    if centerBasedPos[0] > rightedge + margin:
        return False
    if centerBasedPos[0] < leftedge - margin:
        return False
    if centerBasedPos[1] > topedge + margin:
        return False
    if centerBasedPos[1] < bottomedge - margin:
        return False
    return True

def rendergame():
    display.fill(BLACK)
    drawGrid(zoom)
    for cellPos, cell in cells.items():
        if cell[0]:
            drawCell(cellPos, True)   
    UI.drawElements()
    pg.display.flip()

def drawGrid(spacing: int):
    for i in range(leftedge // spacing * spacing - m.ceil(spacing / 2), (2 + rightedge // spacing) * spacing, spacing):
        pg.draw.rect(display, GRAY, (convert.centerbased.x(i - origin[0] % spacing), convert.centerbased.y(topedge), 1, display.get_height()))
    for i in range(bottomedge // spacing * spacing - m.ceil(spacing / 2), (2 + topedge // spacing) * spacing, spacing):
        pg.draw.rect(display, GRAY, (convert.centerbased.x(leftedge), convert.centerbased.y(i - origin[1] % spacing), display.get_width(), 1))
        
def drawCell(cellPos: tuple, isLive: bool):
    COLOR = tuple(((color ^ isLive) % 2 ^ True) * 255 for color in WHITE)
    if isOnScreen((convert.cornerbased.x(convert.cellPos.x(cellPos[0])), convert.cornerbased.y(convert.cellPos.y(cellPos[1]))), zoom):
        pg.draw.rect(display, COLOR, (convert.cellPos.x(cellPos[0]), convert.cellPos.y(cellPos[1]), zoom - 1, zoom - 1))

def handleLeftClick(event):
    global leftMouseHeld
    for layer in range(3):
        for button in UI.UIElements[f"layer{layer}"]["button"]:
            if button.displayFlag:
                if button.rect.collidepoint(event.pos) and not (button.interactableWhilePaused ^ isPaused):
                    leftMouseHeld = True
                    while leftMouseHeld:
                        for Event in pg.event.get():
                            if Event.type == pg.MOUSEBUTTONUP and Event.button == 1:
                                leftMouseHeld = False
                                if button.rect.collidepoint(Event.pos):
                                    button.HandleInteraction()
                                return
                else:
                    continue
    else:
        isCreatingCells = None
        if not isPaused:
            previousCells = {}
            leftMouseHeld = True
            while leftMouseHeld:
                selectedCell: tuple[int] = (convert.realPos.x(pg.mouse.get_pos()[0]), convert.realPos.y(pg.mouse.get_pos()[1]))
                if selectedCell not in previousCells:
                    if isCreatingCells != True and selectedCell in cells:
                        removeCell(selectedCell)
                        drawCell(selectedCell, False)
                        UI.drawElements()
                        pg.display.flip()
                        isCreatingCells = False
                    elif isCreatingCells != False:
                        addCell(selectedCell, True)
                        drawCell(selectedCell, True)
                        UI.drawElements()
                        pg.display.flip()
                        isCreatingCells = True
                    previousCells.setdefault(selectedCell, [])
                for Event in pg.event.get():
                    if Event.type == pg.MOUSEBUTTONUP and Event.button == 1:
                        leftMouseHeld = False

def invertColors():
    global BLACK, WHITE, isDarkMode
    WHITE, BLACK = BLACK, WHITE
    isDarkMode = not(isDarkMode)
    for layer in range(3):
        for elementType in UI.UIElements[f"layer{layer}"]:
            for element in UI.UIElements[f"layer{layer}"][elementType]:
                if element != transluscentBackground:
                    try:
                        element.initialColor = tuple(255 - c for c in element.initialColor)
                        element.color = tuple(255 - c for c in element.color)
                    except:
                        try:
                            element["color"] = tuple(255 - c for c in element["color"])
                        except:
                            pass

                    try:
                        element.textColor = tuple(255 - c for c in element.textColor)
                    except:
                        try:
                            element["textColor"] = tuple(255 - c for c in element["textColor"])
                        except:
                            pass

                    try:
                        element.hoverColor = tuple(255 - c for c in element.hoverColor)
                    except:
                        continue
    if isDarkMode:
        darkModeButton.initialColor = GRAY
        lightModeButton.initialColor = BLACK
        darkModeButton.hoverColor = GRAY
        lightModeButton.hoverColor = WHITE
        darkModeButton.textColor = WHITE
        lightModeButton.textColor = GRAY
    else:
        lightModeButton.initialColor = GRAY
        darkModeButton.initialColor = WHITE
        lightModeButton.hoverColor = GRAY
        darkModeButton.hoverColor = BLACK
        darkModeButton.textColor = GRAY
        lightModeButton.textColor = BLACK

#Button Actions
def pause():
    global isPaused
    isPaused = True
    UI.setElementVisibility([menuRect, resumeButton, pauseMenuText, transluscentBackground, controlsButton, apperanceRect, quitButton, apperanceText, darkModeButton, lightModeButton], True)

def resume():
    global isPaused
    isPaused = False
    UI.setElementVisibility([menuRect, resumeButton, pauseMenuText, transluscentBackground, controlsButton, apperanceRect, quitButton, apperanceText, darkModeButton, lightModeButton], False)

def back():
    UI.setElementVisibility([backButton, controlsMenuText, keyboardButton, mouseButton], False)
    UI.setElementVisibility([pauseMenuText, resumeButton, controlsButton, apperanceRect, quitButton, apperanceText, darkModeButton, lightModeButton], True)

def keyboardMouseBack():
    UI.setElementVisibility([keyboardMouseBackButton, keyboardControlsMenuText, mouseControlsMenuText], False)
    UI.setElementVisibility([backButton, controlsMenuText, keyboardButton, mouseButton], True)

def controlsButtonLogic():
    UI.setElementVisibility([pauseMenuText, resumeButton, controlsButton, apperanceRect, quitButton, apperanceText, darkModeButton, lightModeButton], False)
    UI.setElementVisibility([backButton, controlsMenuText, keyboardButton, mouseButton], True)

def keyboardControlsButtonLogic():
    UI.setElementVisibility([controlsMenuText, keyboardButton, mouseButton, backButton], False)
    UI.setElementVisibility([keyboardControlsMenuText, keyboardMouseBackButton], True)

def mouseControlsButtonLogic():
    UI.setElementVisibility([controlsMenuText, mouseButton, keyboardButton, backButton], False)
    UI.setElementVisibility([mouseControlsMenuText, keyboardMouseBackButton], True)

def setDarkMode():
    if not(isDarkMode):
        invertColors()

def setLightMode():
    if isDarkMode:
        invertColors()

def quit():
    global running
    running = False

cells = {}
UI = UIWrapper()

menuRect = UI.addRect(30.0, 5.0, 40.0, 90.0, WHITE, False, 2)
transluscentBackground = UI.addRect(0.0, 0.0, 100.0, 100.0, (0, 0, 0, 200), False, 1)
pauseMenuText = UI.addText("Pause Menu", BLACK, 50.0, 7.0, "freesansbold.ttf", 10.0, False, 2)
controlsMenuText = UI.addText("Controls", BLACK, 50.0, 7.0, "freesansbold.ttf", 10.0, False, 2)
keyboardControlsMenuText = UI.addText("Keyboard Controls", BLACK, 50.0, 7.0, "freesansbold.ttf", 8.0, False, 2)
mouseControlsMenuText = UI.addText("Mouse Controls", BLACK, 50.0, 7.0, "freesansbold.ttf", 8.0, False, 2)
pauseButton = UI.addButton(1.0, 1.0, 20.0, 10.0, "Menu", "freesansbold.ttf", 8.0, BLACK, WHITE, GRAY, True, False, 0, pause)
resumeButton = UI.addButton(40.0, 19.0, 20.0, 10.0, "Resume", "freesansbold.ttf", 8.0, WHITE, BLACK, GRAY, False, True, 2, resume)
controlsButton = UI.addButton(40.0, 31.0, 20.0, 10.0, "Controls", "freesansbold.ttf", 8.0, WHITE, BLACK, GRAY, False, True, 2, controlsButtonLogic)
backButton = UI.addButton(40.0, 19.0, 20.0, 10.0, "Back", "freesansbold.ttf", 8.0, WHITE, BLACK, GRAY, False, True, 2, back)
keyboardMouseBackButton = UI.addButton(40.0, 19.0, 20.0, 10.0, "Back", "freesansbold.ttf", 8.0, WHITE, BLACK, GRAY, False, True, 2, keyboardMouseBack)
keyboardButton = UI.addButton(32.5, 31.0, 35.0, 10.0, "Keyboard", "freesansbold.ttf", 8.0, WHITE, BLACK, GRAY, False, True, 2, keyboardControlsButtonLogic)
mouseButton = UI.addButton(32.5, 43.0, 35.0, 10.0, "Mouse", "freesansbold.ttf", 8.0, WHITE, BLACK, GRAY, False, True, 2, mouseControlsButtonLogic)
apperanceRect = UI.addRect(35.0, 43.0, 30.0, 38.0, GRAY, False, 2)
apperanceText = UI.addText("Apperance", BLACK, 50.0, 45.0, "freesansbold.ttf", 10.0, False, 2)
darkModeButton = UI.addButton(37.5, 57.0, 25.0, 10.0, "Dark Mode", "freesansbold.ttf", 8.0, WHITE, GRAY, GRAY, False, True, 2, setDarkMode)
lightModeButton = UI.addButton(37.5, 69.0, 25.0, 10.0, "Light Mode", "freesansbold.ttf", 8.0, GRAY, BLACK, WHITE, False, True, 2, setLightMode)
quitButton = UI.addButton(40.0, 83.0, 20.0, 10.0, "Quit", "freesansbold.ttf", 8.0, WHITE, BLACK, GRAY, False, True, 2, quit)

#def tenKsquares():
#    for i in range(1000):
#        for j in range(1000):
#            addCell((i, j), True)
#
#print(f"time taken to generate squares: {timeit.timeit(tenKsquares, number=1)}")

running: bool = True
while running:
    centerx, centery = m.floor(display.get_width() / 2), m.ceil(display.get_height() / 2) - 1 #cornerbased
    rightedge, leftedge, topedge, bottomedge = int(convert.cornerbased.x(display.get_width() - 1)), int(convert.cornerbased.x(0)), int(convert.cornerbased.y(0)), int(convert.cornerbased.y(display.get_height() -1))
    furthestnegedge, furthestposedge = min((leftedge, bottomedge)), max((rightedge, topedge))

    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_r:
                origin = [0, 0]
            if event.key == pg.K_g:
                advanceGeneration()
                #print(f"time taken to update squares: {timeit.timeit(getImportantCells, number=1)} + {timeit.timeit(applyRules, number=1)}")

        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1:
                handleLeftClick(event)
                rendergame()

            elif event.button == 4:
                if zoom < 80:
                    zoom += 2

            elif event.button == 5:
                if zoom > 10:
                   zoom -= 2

            if event.button == 3:
                anchor = pg.mouse.get_pos()
                rightMouseHeld = True
    rendergame()

    while rightMouseHeld:
        for event in pg.event.get():
            if event.type == pg.MOUSEBUTTONUP and event.button == 3:
                rightMouseHeld = False
        anchorTo = pg.mouse.get_pos()
        origin[0] += anchor[0] - anchorTo[0]
        origin[1] -= anchor[1] - anchorTo[1]
        anchor = anchorTo
        rendergame()

pg.quit()
