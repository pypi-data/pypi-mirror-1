from pandac.PandaModules import loadPrcFileData
loadPrcFileData("", "framebuffer-multisample 1")
loadPrcFileData("", "text-minfilter linear")
loadPrcFileData("", "text-pixels-per-unit 50")
#loadPrcFileData("", "window-type none")
from direct.showbase.DirectObject import DirectObject
from pandac.PandaModules import WindowProperties
from pandac.PandaModules import NodePath
from pandac.PandaModules import Vec4, Vec3
from pandac.PandaModules import MouseAndKeyboard, MouseWatcher, ModifierButtons, ButtonThrower, MouseSubregion
from pandac.PandaModules import PGTop, PGMouseWatcherBackground
from pandac.PandaModules import AmbientLight,PointLight
from pandac.PandaModules import Material
from pandac.PandaModules import AntialiasAttrib
from pandac.PandaModules import CollisionTraverser, CollisionHandlerQueue, CollisionNode, CollisionRay
from pandac.PandaModules import GeomNode
from pandac.PandaModules import TextureStage
from direct.gui.DirectGui import DGG
from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectSlider import DirectSlider
from direct.gui.DirectScrolledList import DirectScrolledList
from direct.gui.DirectLabel import DirectLabel
from direct.gui.DirectButton import DirectButton
from direct.gui.OnscreenText import OnscreenText
from pandac.PandaModules import TextNode
from jubatu import commands
import os
import math
import logging
import gettext
from jubatu import util

# Load the translations file for the preferred language
lang = gettext.translation('frontend', os.path.join(os.path.dirname(__file__), 'i18n'), languages=util.get_preferred_languages(), fallback=True)
# A game module MUST not use the lang.install() function, as it would override the default language for the core
_ = lang.ugettext 


_3DREGIONLIMIT = 0.8
INITIAL_CAMERA_HORIZONTAL_ANGLE = 0.78
INITIAL_CAMERA_ZENITH_ANGLE = 0.65
INITIAL_CAMERA_DISTANCE = 23

PIECE_MODELS = {
                "pawn":"models/pawn.egg",
                "rook":"models/rook.egg",
                "knight":"models/knight.egg",
                "bishop":"models/bishop.egg",
                "queen":"models/queen.egg",
                "king":"models/king.egg"
                }

 
class Chess3dGui(DirectObject):
    """Class implementing the 3D-GUI used as front-end in the chess module.
    
    In general, this GUI is intended to work as a 'dummie' gui, not containing any logic associated with the game.
    Due to that, the info about the legit actions a user can take must be passed to the GUI from the main chess module.
    
    The basic function will be this: the main chess module will pass info about the allowed actions to the GUI, then
    it will ask the GUI to 'unlock' the board (throught the 'give_turn' function). After it, the user will be free
    to choose one of the allowed actions; when done so, the GUI will send the info about the user decision to the
    main chess module and will automatically 'lock' it till receiving new orders from the main chess module.
    """
    
    ourTurn = False
    legalMoves = {}
    
    oldPointedSquare = None
    selectedSquare = None
    lastMoveText = None
    
    def __init__(self, match_id, engineCommandsQueue):
        DirectObject.__init__(self)
        self.match_id = match_id
        self.engineCommandsQueue = engineCommandsQueue
        
        wp = WindowProperties()
        wp.setSize(640, 480)
        #wp.setOrigin(512, 128)
        wp.setTitle(_("Chess"));
        
        # Open the toplevel window
        self.__oldAspectRatio = 1
        self.win = base.openWindow(props = wp, aspectRatio = self.__oldAspectRatio)
        base.win = None
        
        self.camLens = base.camLens
        self.win.setClearColor(Vec4(0.6,0.6,0.6,1))
        
        self.render = NodePath('render')
        self.render.setAntialias(AntialiasAttrib.MMultisample,1)
        self.setup_mouse_watchers()                    # Setup input devices & MouseWatchers
        self.setup_layers_and_camera()                  # Setup camera, render2d, camera2d, render2dPG
        self.setup_lights()                           # Setup default lighting
        
        self.modulePath = '/'+os.path.dirname(__file__).replace(':','/').replace(os.sep,'/')
        logging.getLogger("chessEngine").debug("Detected module path: %s", self.modulePath)
        
        self.squareRoot = self.render.attachNewNode("squareRoot")   # the root for all the squares (all the clickable objects)
        self.pieceRoot = self.render.attachNewNode("pieceRoot")    # the root for all the pieces
        
        # Material for the board
        boardMaterial = Material("SquareMaterial")
        boardMaterial.setAmbient(Vec4(1,1,1,1))
        boardMaterial.setDiffuse(Vec4(1,1,1,1))
        boardMaterial.setSpecular(Vec4(0.6,0.6,0.6,1))
        boardMaterial.setShininess(0.25)
        
        # Board's frame
        boardFrameTex = loader.loadTexture(os.path.join(self.modulePath, "textures/oakburlsq.jpg"))
        boardFrame = loader.loadModel(os.path.join(self.modulePath, "models/boardframe.egg"))
        boardFrame.setMaterial(boardMaterial,1)
        boardFrame.setTexture(boardFrameTex)
        boardFrame.reparentTo(self.render)
        boardFrame.setPos(0,0,0)

        # White & black textures for the squares
        wsTex = loader.loadTexture(os.path.join(self.modulePath, "textures/lacewood.jpg"))
        bsTex = loader.loadTexture(os.path.join(self.modulePath, "textures/walnutblksq.jpg"))
                
        # squares
        for i in range(8):
            for j in range(8):
                square = loader.loadModel(os.path.join(self.modulePath, "models/square.egg"))
                square.setMaterial(boardMaterial,1)
                square.setPos(i,j,0)
                if (i^j)%2==0:
                    square.setTexture(bsTex)
                else:
                    square.setTexture(wsTex)
                square.reparentTo(self.squareRoot)
        
        
        # Material for the pieces
        self.pieceMaterial = Material("PieceMaterial")
        self.pieceMaterial.setAmbient(Vec4(1,1,1,1))
        self.pieceMaterial.setDiffuse(Vec4(1,1,1,1))
        self.pieceMaterial.setSpecular(Vec4(1,1,1,1))
        self.pieceMaterial.setShininess(10)

        # Pieces' textures
        self.wpTex = loader.loadTexture(os.path.join(self.modulePath, "textures/oakwhitesq.jpg"))
        self.bpTex = loader.loadTexture(os.path.join(self.modulePath, "textures/burloaksq.jpg"))
                
        # Panda3d's GUI controls
        self.frame = DirectFrame(frameColor=(0.5,0.3,0.3,1), frameSize=(2*_3DREGIONLIMIT-1,1,-1,1), relief=DGG.FLAT)
        self.frame.reparentTo(self.render2dPG)
                
        self.horizontalAngleSlider=DirectSlider(value=INITIAL_CAMERA_HORIZONTAL_ANGLE, range=(0,2*math.pi), pageSize=0.314, relief=DGG.GROOVE, borderWidth=(0.01,0.01), frameSize=(2*_3DREGIONLIMIT-1,1,0.9,1), thumb_borderWidth=(0.02,0.02), thumb_frameSize=(0,0.06,-0.03,0.03), thumb_relief=DGG.RIDGE, frameColor=(0.9,0.9,0.9,1))
        self.horizontalAngleSlider.reparentTo(self.frame)
        
        self.zenithAngleSlider=DirectSlider(value=INITIAL_CAMERA_ZENITH_ANGLE, range=(0.01,math.pi/2), pageSize=0.078, relief=DGG.GROOVE, borderWidth=(0.01,0.01), frameSize=(2*_3DREGIONLIMIT-1,1,0.8,0.9), thumb_borderWidth=(0.02,0.02), thumb_frameSize=(0,0.06,-0.03,0.03), thumb_relief=DGG.RIDGE, frameColor=(0.9,0.9,0.9,1))
        self.zenithAngleSlider.reparentTo(self.frame)
        
        self.distanceSlider=DirectSlider(value=INITIAL_CAMERA_DISTANCE, range=(15,25), pageSize=0.5, relief=DGG.GROOVE, borderWidth=(0.01,0.01), frameSize=(2*_3DREGIONLIMIT-1,1,0.7,0.8), thumb_borderWidth=(0.02,0.02), thumb_frameSize=(0,0.06,-0.03,0.03), thumb_relief=DGG.RIDGE, frameColor=(0.9,0.9,0.9,1))
        self.distanceSlider.reparentTo(self.frame)
        
        self.horizontalAngleSlider["command"]=self.set_camera_pos
        self.zenithAngleSlider["command"]=self.set_camera_pos
        self.distanceSlider["command"]=self.set_camera_pos
        
        self.moveList = DirectScrolledList(numItemsVisible=14, forceHeight = 0.068, relief=DGG.SUNKEN, borderWidth=(0.01,0), frameSize=(2*_3DREGIONLIMIT-1,1,-0.5,0.59), incButton_borderWidth=(0.01,0.01), incButton_relief=DGG.RAISED, decButton_frameSize= (_3DREGIONLIMIT*2-1,1,0.59,0.69), decButton_borderWidth=(0.01,0.01), decButton_relief=DGG.RAISED, incButton_frameSize= (_3DREGIONLIMIT*2-1,1,-0.6,-0.5))
        self.moveList.reparentTo(self.render2dPG)

        drawButtonText = _("Propose/Claim draw")
        self.drawButton = DirectButton(text = drawButtonText, text_pos=(_3DREGIONLIMIT,-0.76+0.04*len(drawButtonText.splitlines())), text_scale=(0.05,0.05), frameSize=(2*_3DREGIONLIMIT-1,1,-0.8,-0.6), relief = DGG.RAISED, borderWidth=(0.01,0.01), pressEffect = 1, state = DGG.DISABLED, command=self.propose_or_claim_draw)
        self.drawButton.reparentTo(self.render2dPG)
        
        resignButtonText = _("Resign")
        self.resignButton = DirectButton(text = resignButtonText, text_pos=(_3DREGIONLIMIT,-0.96+0.04*len(resignButtonText.splitlines())), text_scale=(0.05,0.05), frameSize=(2*_3DREGIONLIMIT-1,1,-1,-0.8), relief = DGG.RAISED, borderWidth=(0.01,0.01), pressEffect = 0, state = DGG.DISABLED, command=self.resign)
        self.resignButton.reparentTo(self.render2dPG)
        
        # Neccesary objects to implement collision logic
        self.picker= CollisionTraverser()
        self.pickerQueue=CollisionHandlerQueue()
        self.pickerNode=CollisionNode('pickerRay')
        self.pickerNP=self.render.attachNewNode(self.pickerNode)
        self.pickerNode.setFromCollideMask(GeomNode.getDefaultCollideMask())
        self.pickerRay=CollisionRay()
        self.pickerNode.addSolid(self.pickerRay)
        self.picker.addCollider(self.pickerNP, self.pickerQueue)
        
        # Set up material and texture to highlight pointed squares
        self.highlightMaterial = Material("HighlightMaterial")
        self.highlightMaterial.setAmbient(Vec4(0,0,0,1))
        self.highlightMaterial.setDiffuse(Vec4(0,0,0,1))
        self.highlightMaterial.setEmission(Vec4(0.4,0.4,0.9,1))
        
        self.highlightTexture = loader.loadTexture(os.path.join(self.modulePath, "textures/highlight.jpg"))
                
        self.highlightTs = TextureStage('tschess')
        self.highlightTs.setMode(TextureStage.MAdd)
        self.highlightTs.setSort(10000)
        
        # Initial camera positioning
        self.set_camera_pos()
        
        self.window_event(self.win)
        
        # Handles window events (resizing, mostly)
        self.accept('window-event', self.window_event)

        # Handles mouse movement (highlighting of squares, mainly)
        self.mouse_task = taskMgr.add(self.mouse_task, 'mouse_task')
        # Handles selection of squares
        self.accept("mouse1", self.select_square)       #left-click selects a square


    def set_camera_pos(self):
        """Set the camera position taking the coordinates from the sliders' values."""
        
        self.camera.setPos(self.distanceSlider['value']*math.cos(self.horizontalAngleSlider['value'])*math.sin(self.zenithAngleSlider['value']),
            self.distanceSlider['value']*math.sin(self.horizontalAngleSlider['value'])*math.sin(self.zenithAngleSlider['value']), 
            self.distanceSlider['value']*math.cos(self.zenithAngleSlider['value']))        
        self.camera.lookAt(0,0,0)
        
    def set_title(self, title):
        """ Set the GUI window's title."""
        
        winProps = WindowProperties()
        winProps.setTitle(title)
        self.win.requestProperties(winProps)
    
    def set_piece(self, piece, colour, col, row):
        """Set a piece of a given type and a given colour in a given position.
        
        piece -- The type of piece; this has to be considered in a lax way, as 'black' is a legit choice. See the
            keys used in the PIECE_MODELS structure above.
        colour -- The colour of the piece: "white" or "black". Unimportant if piece=="blank"
        col -- Column where the piece have to be set.
        row -- Row where the piece have to be set.
        """
        
        logging.getLogger("chessEngine").debug("%s, %s, %d, %d", piece, colour, col, row)
        
        # firstly, let's see if there is any piece in that location
        self.pickerNP.detachNode()
        self.pickerNP=self.render.attachNewNode(self.pickerNode)
        self.pickerRay.setOrigin(col-3.5, row-3.5, 0)
        logging.getLogger("chessEngine").debug("Ray origin: %s", self.pickerRay.getOrigin())
        self.pickerRay.setDirection(Vec3(0,0,1))
        self.picker.traverse(self.pieceRoot)
        if self.pickerQueue.getNumEntries() > 0:  # if so, delete it
            logging.getLogger("chessEngine").debug("Piece picked!")
            previousPiece=self.pickerQueue.getEntry(0).getIntoNodePath()
            previousPiece.removeNode()
        
        # now, let's put the new piece
        if piece!="blank":
            pieceModel = loader.loadModel(os.path.join(self.modulePath, PIECE_MODELS[piece]))
            pieceModel.setMaterial(self.pieceMaterial,1)
            if colour=="white":
                pieceModel.setTexture(self.wpTex)
            elif colour=="black":
                pieceModel.setTexture(self.bpTex)
                pieceModel.setHpr(180,0,0)
            else:
                logging.getLogger("chessEngine").error("Inappropriate colour parameter.")
            pieceModel.setPos(col-3.5, row-3.5,0)
            pieceModel.setTag("piece", "true")
            pieceModel.reparentTo(self.pieceRoot)
            
    def give_turn(self, legalMoves, canClaimDraw=False):
        """'Unlock' the board, allowing the user to take his turn by choosing one of the allowed actions."""
        
        logging.getLogger("chessEngine").debug("Legal moves: %s", legalMoves)
        self.legalMoves = legalMoves
        self.canClaimDraw = canClaimDraw
        self.ourTurn = True
        self.resignButton['state']=DGG.NORMAL
        self.drawButton['relief']=DGG.RAISED
        self.drawButton['state']=DGG.NORMAL
        
    def finish_game(self, info):
        """Finish the match, showing in screen information about the game-end conditions."""

        self.disable_board()

        OnscreenText(text=_("End of match"),
                    style=1, fg=(0 ,0,0,1), bg=(1,1,1,0.7),
                    pos=(-0.9,0.8), scale = .15, align=TextNode.ALeft, parent=self.render2dPG)
        OnscreenText(text=info,
                    style=1, fg=(0 ,0,0,1), bg=(1,1,1,0.7),
                    pos=(-0.9,0.6), scale = .1, align=TextNode.ALeft, parent=self.render2dPG)
        
    def resign(self):
        """Handle the resign of the user."""
        
        resignAction = {'match-id':self.match_id, 'action':'resign'}
        self.return_action(resignAction)
        
    def propose_or_claim_draw(self):
        """If the conditions of the match allow the user to claim draw, it's claimed. Otherwise, we propose a draw agreement."""
        
        if self.canClaimDraw:
            claimDrawAction = {'match-id':self.match_id, 'action':'claim draw'}
            self.return_action(claimDrawAction)
        else:
            if self.drawButton['relief']==DGG.RAISED:
                self.drawButton['relief']=DGG.SUNKEN
            else:
                self.drawButton['relief']=DGG.RAISED
            
    def request_draw_proposal_answer(self):
        """Ask the user to reply to a draw proposal sended by our adversary."""
        
        self.disable_board()
        
        self.drawInfoHeader = OnscreenText(text="Draw proposed by opponent player.",
                    style=1, fg=(0,0,0,1), bg=(1,1,1,0.7),
                    pos=(_3DREGIONLIMIT-1,0.8), scale = .1, align=TextNode.ACenter, parent=self.render2dPG)

        self.acceptDraw = DirectButton(text = _("Accept"), text_pos=(_3DREGIONLIMIT-1,0.48), text_scale=(0.05,0.05), frameColor=(1,1,1,0.7), frameSize=(_3DREGIONLIMIT/4-1,_3DREGIONLIMIT*7/4-1,0.4,0.6), relief = DGG.RAISED, borderWidth=(0.01,0.01), pressEffect = 1, command=self.draw_accepted)
        self.acceptDraw.reparentTo(self.render2dPG)

        self.declineDraw = DirectButton(text = _("Decline"), text_pos=(_3DREGIONLIMIT-1,0.28), text_scale=(0.05,0.05), frameColor=(1,1,1,0.7), frameSize=(_3DREGIONLIMIT/4-1,_3DREGIONLIMIT*7/4-1,0.2,0.4), relief = DGG.RAISED, borderWidth=(0.01,0.01), pressEffect = 1, command=self.draw_declined)
        self.declineDraw.reparentTo(self.render2dPG)
        
    def draw_accepted(self):
        """Handle the acceptance by the local user of a draw agreement proposed by our adversary."""
        
        self.drawInfoHeader.destroy()
        self.acceptDraw.destroy()
        self.declineDraw.destroy()

        acceptDrawAction = {'match-id':self.match_id, 'action':'accept draw'}
        self.engineCommandsQueue.put(commands.JuLocalTurnAction(acceptDrawAction))
        
    def draw_declined(self):
        """Handle the rejection by the local user of a draw agreement proposed by our adversary."""
        
        self.drawInfoHeader.destroy()
        self.acceptDraw.destroy()
        self.declineDraw.destroy()

        declineDrawAction = {'match-id':self.match_id, 'action':'decline draw'}
        self.engineCommandsQueue.put(commands.JuLocalTurnAction(declineDrawAction))
        
    def request_promotion_piece(self):
        """Ask the user to choose a promotion piece."""
        
        self.disable_board()
        
        self.promotionInfoHeader = OnscreenText(text=_("Promote pawn to:"),
                    style=1, fg=(0,0,0,1), bg=(1,1,1,0.7),
                    pos=(_3DREGIONLIMIT-1,0.8), scale = .1, align=TextNode.ACenter, parent=self.render2dPG)
        self.promoteToQueenButton = DirectButton(text = _("Queen"), text_pos=(_3DREGIONLIMIT-1,0.48), text_scale=(0.05,0.05), frameColor=(1,1,1,0.7), frameSize=(_3DREGIONLIMIT/4-1,_3DREGIONLIMIT*7/4-1,0.4,0.6), relief = DGG.RAISED, borderWidth=(0.01,0.01), pressEffect = 1, command=self.make_promotion_handler("queen"))
        self.promoteToRookButton = DirectButton(text = _("Rook"), text_pos=(_3DREGIONLIMIT-1,0.28), text_scale=(0.05,0.05), frameColor=(1,1,1,0.7), frameSize=(_3DREGIONLIMIT/4-1,_3DREGIONLIMIT*7/4-1,0.2,0.4), relief = DGG.RAISED, borderWidth=(0.01,0.01), pressEffect = 1, command=self.make_promotion_handler("rook"))
        self.promoteToBishopButton = DirectButton(text = _("Bishop"), text_pos=(_3DREGIONLIMIT-1,0.08), text_scale=(0.05,0.05), frameColor=(1,1,1,0.7), frameSize=(_3DREGIONLIMIT/4-1,_3DREGIONLIMIT*7/4-1,0.0,0.2), relief = DGG.RAISED, borderWidth=(0.01,0.01), pressEffect = 1, command=self.make_promotion_handler("bishop"))
        self.promoteToKnightButton = DirectButton(text = _("Knight"), text_pos=(_3DREGIONLIMIT-1,-0.12), text_scale=(0.05,0.05), frameColor=(1,1,1,0.7), frameSize=(_3DREGIONLIMIT/4-1,_3DREGIONLIMIT*7/4-1,-0.2,0.0), relief = DGG.RAISED, borderWidth=(0.01,0.01), pressEffect = 1, command=self.make_promotion_handler("knight"))
        
        self.promoteToQueenButton.reparentTo(self.render2dPG)
        self.promoteToRookButton.reparentTo(self.render2dPG)
        self.promoteToBishopButton.reparentTo(self.render2dPG)
        self.promoteToKnightButton.reparentTo(self.render2dPG)
        
    def make_promotion_handler(self, piece):
        """Return a 'promotino handler' with an implicit parameter 'piece'"""
        
        return lambda : self.promote_to(piece)
    def promote_to(self, piece):
        """Handle the choice of the user for the piece to use in exchange for a promoted pawn.
        
        piece -- Piece chosen by the user.
        """
        
        self.promotionInfoHeader.destroy()
        self.promoteToQueenButton.destroy()
        self.promoteToRookButton.destroy()
        self.promoteToBishopButton.destroy()
        self.promoteToKnightButton.destroy()
        
        promoteAction = {'match-id':self.match_id, 'action':'promotion', 'piece':piece}
        self.engineCommandsQueue.put(commands.JuLocalTurnAction(promoteAction))
        
    def show_move_text(self, moveText):
        """Display, in the right listbox, the text corresponding to a movement.
        
        Note that the formatting of the text, together with the management of when it must be displayed, it's
        competence of the main chess module.
        """
        
        #font=loader.loadFont('cmtt12.egg')
        if moveText[0]==",":  # black side's move
            if self.lastMoveText is not None:
                moveText = self.lastMoveText["text"]+moveText
                self.moveList.removeItem(self.lastMoveText)
            
        self.lastMoveText = DirectLabel(text=moveText, frameSize=(2*_3DREGIONLIMIT-0.94,0.98,0,0), text_scale=(0.05,0.05), text_pos=(2*_3DREGIONLIMIT-0.97,0.5), text_align=TextNode.ALeft)
        self.moveList.addItem(self.lastMoveText, True)
        self.moveList.scrollBy(500)  # go to the end of the list
        
    def setup_mouse_watchers(self):
        """Create the mouse watchers used by Panda3d.
        
        A couple of mouse watchers are created: one affecting only to the 3d-view,
        and other one for all the Panda3D window. The first is convenient for doing 3d-calculations with the mouse
        coordinates; the second one is convenient, by example, if you want to center a Panda3d's gui control in the
        center of the full window.
        """
        
        self.buttonThrowers = []
        name = self.win.getInputDeviceName(0)
        mk = base.dataRoot.attachNewNode(MouseAndKeyboard(self.win, 0, name))
        # first MouseWatcher to catch GUI mouse events in the full window
        self.mouseWatcherGuiLayer = mk.attachNewNode(MouseWatcher(name))
        msr = self.mouseWatcherGuiLayer.attachNewNode(MouseSubregion(name))
        msr.node().setDimensions(0,_3DREGIONLIMIT,0,1)
        # second MouseWatcher, limited to the 3D view region
        self.mouseWatcher3dView = msr.attachNewNode(MouseWatcher(name+"3dView"))

        bt = self.mouseWatcher3dView.attachNewNode(ButtonThrower(name))
        mods = ModifierButtons()
        bt.node().setModifierButtons(mods)
        self.buttonThrowers.append(bt)
        
    def setup_layers_and_camera(self):     # Setup camera, render2d, camera2d, render2dPG
        self.camera = base.camList[-1]
        self.camera.node().getDisplayRegion(0).setDimensions(0,_3DREGIONLIMIT,0,1)
        self.camera.setScale(_3DREGIONLIMIT,1.0,1.0)
        self.camera.reparentTo(self.render)    
        
        self.render2d = NodePath('render2d')

        # Set up some overrides to turn off certain properties which
        # we probably won't need for 2-d objects.

        self.render2d.setDepthTest(0)
        self.render2d.setDepthWrite(0)
        self.render2d.setMaterialOff(1)
        self.render2d.setTwoSided(1)

        self.camera2d = base.makeCamera2d(self.win)
        self.camera2d.reparentTo(self.render2d)
        self.render2dPG = self.render2d.attachNewNode(PGTop("render2dPG"))
        self.render2dPG.node().setMouseWatcher(self.mouseWatcherGuiLayer.node())
        self.mouseWatcherGuiLayer.node().addRegion(PGMouseWatcherBackground())
        
    def setup_lights(self):    #This function sets up some default lighting
        """Set up the lights for the 3D scene.
        
        After some testing, i have come to the conclusion that an ambientLight plus a PointLight attached to the
        camera is a good choice, but i'm not an expert in 3d scenes lightning, so i'm guessing this could be 
        better tuned by someone with more experience than me.
        """
        
        ambientLight = AmbientLight("ambientLight")
        ambientLight.setColor(Vec4(0.1, 0.1, 0.1, 1))
        al = self.render.attachNewNode(ambientLight)
        self.render.setLight(al)
        
        pointLight = PointLight( "directionalLightCamera")
        pointLight.setColor(Vec4( 1.0, 1.0, 1.0, 1 ))
        cameraLight = self.camera.attachNewNode(pointLight) 
        self.render.setLight(cameraLight)
        
    def window_event(self, win):         # Handler for window-related events (resizing, etc...)
        """Handle a window-related event."""
        
        if win == self.win:
            aspectRatio = base.getAspectRatio(self.win)
            if aspectRatio != self.__oldAspectRatio:
                self.__oldAspectRatio = aspectRatio
                # Fix up some things that depends on the aspectRatio
                logging.getLogger("chessEngine").debug("New aspect ratio: %s", aspectRatio)
                self.camera.node().getLens().setAspectRatio(aspectRatio)
                
            messenger.send("aspectRatioChanged")
                  
    def get_pointed_square(self):
        """Get the square to which the user is currently pointing with the mouse."""
        
        pointedSquare = None
        if self.mouseWatcher3dView.node().hasMouse():
            mpos = self.mouseWatcher3dView.node().getMouse()
            self.pickerNP.detachNode()
            self.pickerNP=self.camera.attachNewNode(self.pickerNode)
            self.pickerRay.setFromLens(self.camera.node(), mpos.getX(),mpos.getY())
            self.picker.traverse(self.squareRoot)
            if self.pickerQueue.getNumEntries() > 0:
                self.pickerQueue.sortEntries()
                pointedSquare=self.pickerQueue.getEntry(0).getIntoNodePath()
        
        return pointedSquare
        
    def mouse_task(self, task):
        """Handle mouse's events
        
        The main task of this handler will be to appropriately highlight the squares to which the user is pointing to.
        """
        
        if not self.ourTurn:
            return task.cont
        
        pointedSquare = self.get_pointed_square()
        if pointedSquare is not None:            
            squarePosition = self.render.getRelativePoint(pointedSquare, Vec3(0,0,0))
            if self.selectedSquare is not None:
                selectedPosition = self.render.getRelativePoint(self.selectedSquare, Vec3(0,0,0))
                if not (squarePosition.getX(), squarePosition.getY()) in self.legalMoves[(int(selectedPosition.getX()),int(selectedPosition.getY()))]:
                    pointedSquare = None
                    self.clear_previously_pointed_square()
            else:
                if not self.legalMoves.has_key((int(squarePosition.getX()),int(squarePosition.getY()))):
                    pointedSquare = None
                    self.clear_previously_pointed_square()
                    
            if pointedSquare is not None:
                if pointedSquare!=self.oldPointedSquare:
                    self.clear_previously_pointed_square()
                    
                    pointedSquare.setTexture(self.highlightTs, self.highlightTexture)
                    pointedSquare.setMaterial(self.highlightMaterial,1)
                    
                    self.oldPointedSquare=pointedSquare
        else:
            self.clear_previously_pointed_square()
                
        return task.cont
    
    def clear_previously_pointed_square(self):
        """Helper function to clear the hightligh of a previously highlighted square."""
        
        if (self.oldPointedSquare is not None) and (self.oldPointedSquare != self.selectedSquare):
            self.oldPointedSquare.clearMaterial()
            self.oldPointedSquare.clearTexture()
            self.oldPointedSquare = None
            
    def disable_board(self):
        """'Lock' the board to not allow the user to make movements.
        
        This function will be called normally when it's our adversary's turn or the match has ended.
        """
        
        self.ourTurn = False
        self.resignButton["state"]=DGG.DISABLED
        self.drawButton["state"]=DGG.DISABLED
        
        if self.selectedSquare is not None:
            self.selectedSquare.clearMaterial()
            self.selectedSquare.clearTexture()
            self.selectedSquare = None
        
        self.clear_previously_pointed_square()
            
    def return_action(self, action):
        """Return an action to the main chess module, 'locking' the board till receiving new orders."""
        
        self.disable_board()
        
        self.engineCommandsQueue.put(commands.JuLocalTurnAction(action))
            
    def select_square(self):
        """Select an square, in response to a user action asking to do so (a mouse click, as of now)."""
        
        if not self.ourTurn:
            return
        
        pointedSquare = self.get_pointed_square()
        if pointedSquare is None:
            return
        
        squarePosition = self.render.getRelativePoint(pointedSquare, Vec3(0,0,0))
        squareCoord = (int(squarePosition.getX()), int(squarePosition.getY()))
        
        if self.selectedSquare is None:
            if self.legalMoves.has_key(squareCoord):
                self.selectedSquare = pointedSquare

                self.selectedSquare.setTexture(self.highlightTs, self.highlightTexture)
                self.selectedSquare.setMaterial(self.highlightMaterial,1)
        else:
            if self.selectedSquare == pointedSquare:
                self.selectedSquare.clearMaterial()
                self.selectedSquare.clearTexture()
                self.selectedSquare = None
                self.clear_previously_pointed_square()
                self.oldPointedSquare = pointedSquare
            else:
                selectedPosition = self.render.getRelativePoint(self.selectedSquare, Vec3(0,0,0))
                if squareCoord in self.legalMoves[(selectedPosition.getX(), selectedPosition.getY())]:
                    
                    fromPosition = self.render.getRelativePoint(self.selectedSquare, Vec3(0,0,0))
                    fromPosition = (int(fromPosition.getX()), int(fromPosition.getY()))
                    toPosition = self.render.getRelativePoint(pointedSquare, Vec3(0,0,0))
                    toPosition = (int(toPosition.getX()), int(toPosition.getY()))

                    turnAction = {'match-id':self.match_id, 'action':'movement', 'from':fromPosition, 'to':toPosition, 'draw proposal or claim':(self.drawButton['relief']==DGG.SUNKEN)}
                    self.return_action(turnAction)
