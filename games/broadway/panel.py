import string;

_ = lambda x : x

# Pygame Imports
import pygame
from pygame.locals import *

# Spyral Import
import spyral

# PGU Imports
from pgu import text
from pgu import gui
from pgu import html
from scriptarea import ScriptArea

# Broadway Imports
from constants import *;
import backdrop;
import actor;
import action;

class Panel(gui.Container):
	name= "Generic Panel";
	"""
	A Panel is a PGU *Container* that can be swapped by a *Tab*. There are five
	tabs in Broadway. This class is meant to be subclassed.
	"""
	def __init__(self):
		"""
		Initializes the Panel
		"""
		gui.Container.__init__(self);
		self.owningWidgets= [];
		self.groups= [];
	
	def build(self):
		"""
		Virtual function that is called when the Panel is first given focus. Should be
		used to (re)build any components in the panel.
		"""
		self.add(gui.Image(images['main-panel'], name='panel-image-background'), 0,0);
	
	def tearDown(self):
		"""
		Function that is called when the Panel is losing focus. Should be used
		to remove any built components.
		"""
		for aWidget in self.owningWidgets:
			aWidget.kill();
		self.owningWidgets= [];
		self.groups= [];
		self.kill();
	
	def handleGlobalMouse(self, position, button):
		"""
		Virtual function that can be overriden to handle customized input
		from the mouse when it is clicked anywhere on the screen.
		"""
		pass;
	
	def refreshPanel(self):
		self.tearDown();
		self.build();

class FilePanel(Panel):
	"""
	This panel holds the saving/loading/new buttons, the metadata editing area,
	and the credits label.
	"""
	name= "File";
	
	def __init__(self, script):
		"""
		
		"""
		Panel.__init__(self);
		self.script= script;
		self.testingTable= None;
	
	def doNothing(self):
		pass;
	
	def build(self):
		Panel.build(self);
		fileButtonsTable= gui.Table(width= 120,
									height= geom['panel'].height);
		
		buttons= [( _("New"), "file-button-new", self.openNewDialog),
				  ( _("Open"), "file-button-load", self.openLoadDialog),
				  ( _("Save"), "file-button-save", self.openSaveDialog),
				  ( _("Save As"), "file-button-saveAs", self.openSaveAsDialog),
				  ( _("Export"), "file-button-export", self.checkIfScriptNamed)];
		for aButton in buttons:
			properName, internalName, function= aButton;
			aButton= gui.Button(properName, name=internalName, style={'width': 90, 'height': 32});
			aButton.connect(gui.CLICK, function);
			fileButtonsTable.tr();
			fileButtonsTable.td(aButton, align=0);
			if properName == _("Save"):
				self.saveButton= aButton;
		self.add(fileButtonsTable,0,0);
		self.owningWidgets.append(fileButtonsTable);
		
		logoImage= gui.Image(images['main-logo']);
		logoImage.connect(gui.CLICK, self.openCreditsDialog);
		self.add(logoImage, 160, 70);
		self.owningWidgets.append(logoImage);
		
		#creditsButton= gui.Button(_("Credits"), name= 'file-button-credits', style={'width': 80, 'height': 40});
		#creditsButton.connect(gui.CLICK, self.openCreditsDialog);
		#self.add(creditsButton, 255, 175);
		#self.owningWidgets.append(creditsButton);
		
		fileDocument= gui.Document(width=geom['panel'].width // 2, align=-1);
		
		fileDocument.add(gui.Label(_("Title: ")), align=-1);
		titleInput= gui.Input(name='file-input-title', value=self.script.metadata.title,size=30);
		titleInput.connect(gui.CHANGE, self.modifyScriptMetadata, 'title');
		fileDocument.add(titleInput, align= 1);
		
		fileDocument.space((10,40));
		fileDocument.br(1);
		
		fileDocument.add(gui.Label(_("Author(s): ")), align=-1);
		authorInput= gui.Input(name='file-input-author', value=self.script.metadata.author,size=30);
		authorInput.connect(gui.CHANGE, self.modifyScriptMetadata, 'author');
		fileDocument.add(authorInput, align=1);
		fileDocument.space((10,40));
		fileDocument.br(1);
		
		fileDocument.add(gui.Label(_("Description: ")), align=-1);
		fileDocument.br(1);
		descriptionArea= gui.TextArea(name='file-textArea-description', 
									  value=self.script.metadata.description,
									  width=geom['panel'].width // 2 - 11,
									  height= geom['panel'].height // 3);
		descriptionArea.connect(gui.CHANGE, self.modifyScriptMetadata, 'description');
		fileDocument.add(descriptionArea, align= -1);
		fileDocument.space((10,10));
		
		self.add(fileDocument,500,30);
		
		self.owningWidgets.append(fileDocument);

		
		# languageSelector= gui.Select(name='file-button-language', value=language, cols=2);
		## languageSelector.connect(gui.SELECT, self.changePose);
		# for aLanguage in languages:
			# prettyLanguage= aLanguage.replace('_',' ');
			# languageSelector.add(prettyLanguage, aLanguage);
		# languageSelector.connect(gui.SELECT, self.changeLanguage)
		
		#self.add(languageSelector, 730, 170);
		#self.owningWidgets.append(languageSelector);
		
		self.script.controls["file-button-save"].disabled= not self.script.unsaved;
	
	def openCreditsDialog(self):
		"""
		This will probs be changed to a nice Broadway logo, and then have a
		dialog box pop-up for the credits. For now, whatevs.
		"""
		d= gui.InfoDialog(_("Credits"), information['credits']);
		d.connect(gui.CLOSE, self.script.refreshTheater);
		d.open();
	
	def teacherBackdrop(self):
		teachers = getTeacherList()
		if teachers:
			d = gui.TeacherDialog()
			d.loadTeachers(teachers)
			d.connect(gui.CLOSE, self.script.refreshTheater);
			d.connect(gui.CHANGE, self.loadTeacherBackdrop);
			d.open()
		else:
			d= gui.ConfirmDialog(_("Connection Error"), [_("You are not connected to the internet."),
														 _("Connect and then click Okay below.")])
			def tryAgain():
				d.close()
				self.teacherBackdrop()
			d.connect(gui.CLOSE, self.script.refreshTheater);
			d.okayButton.connect(gui.CLICK, tryAgain)
			d.open();
		
	
	def checkIfScriptNamed(self):
		if self.script.metadata.title and self.script.metadata.author:
			self.openExportDialog()
		else:
			if self.script.metadata.title:
				message = "an Author"
			elif self.script.metadata.author:
				message = "a Title"
			else:
				message = "an Author or Title"
			self.confirmActionDialog(_("Save without %{message}s?") % {"message" : message},
									[ _("You haven't given your script %{message}s.") % {"message" : message},
									  _("Are you sure you want to export it?")],
									okayFunction= self.openExportDialog);
	
	def openExportDialog(self, d=None):
		if d is not None: d.close()
		main = gui.Table()
		
		# Some Image Amount code so we can reference it early
		imageAmountSelector= gui.Select(name='file-select-export-amount', value=_("Few"), cols=1);
		def activateImageAmount(_widget):
			imageAmountSelector.disabled= (_widget.value == "Plain")
		
		# Export Type
		main.tr()		
		main.td(gui.Label(_("Export Type: "), style={'margin': 4}))
		exportTypeSelector= gui.Select(name='file-select-export-fancy', value=_("Fancy"), cols=1);
		exportTypeSelector.connect(gui.SELECT, activateImageAmount);
		exportTypeSelector.add(_("Plain (just text)"), "Plain")
		exportTypeSelector.add(_("Fancy (pictures)"), "Fancy")
		main.td(exportTypeSelector)
		
		# Image Amount
		main.tr()
		main.td(gui.Label(_("Image Amount: "), style={'margin': 4}))
		imageAmountSelector.add(_("Tons"), "Tons")
		imageAmountSelector.add(_("Many"), "Many")
		imageAmountSelector.add(_("Few"), "Few")
		imageAmountSelector.add(_("None"), "None")
		main.td(imageAmountSelector)
		
		# Location
		main.tr()
		main.td(gui.Label(_("Location: "), style={'margin': 4}))
		locationSelector= gui.Select(name='file-select-export-location', value=_("Here"), cols=1);
		locationSelector.add(_("Here"), "Here")
		locationSelector.add(_("Teacher"), "Teacher")
		main.td(locationSelector)
		
		# Okay/Cancel
		main.tr()
		okayButton= gui.Button(_("Okay"), name='file-button-export-okay', style={'margin': 10})
		main.td(okayButton)
		cancelButton= gui.Button(_("Cancel"), name='file-button-export-cancel', style={'margin': 10})
		main.td(cancelButton)
	
		# exportOptions = gui.Document()
		# exportButtons= [(gui.Button(_("Text"), name= 'file-button-export-text', style={'margin':4}), 'text', ['.txt']),
						# (gui.Button(_("HTML"), name= 'file-button-export-html', style={'margin':4}), 'html', ['.html'])]
		##, (gui.Button(_("Video"), name= 'file-button-export-text', style={'margin':4}), 'video', ['.mpeg'])
		d= gui.Dialog(gui.Label(_("Export")), main)
		# for aButton, value, valueType in exportButtons:
			# exportOptions.add(aButton)
			# aButton.connect(gui.CLICK, self.export, value, valueType, d)
		d.connect(gui.CLOSE, self.script.refreshTheater);
		
		cancelButton.connect(gui.CLICK, d.close)
		okayButton.connect(gui.CLICK, self.export, d)
		
		d.open()
	
	def export(self, _widget, dialog):
		fancy = self.script.controls["file-select-export-fancy"].value
		amount = self.script.controls["file-select-export-amount"].value
		location = self.script.controls["file-select-export-location"].value
		
		if fancy == "Fancy" and location == "Teacher" and amount == "Tons":
			d= gui.ConfirmDialog(_("Continue Upload?"), [_("Uploading a script with these settings might take a long time."),
														 _("Continue the upload anyway?")])
			def continueAnyway():
				d.close()
				dialog.close()
				self.exportActual(fancy, amount, location)
			d.connect(gui.CLOSE, self.script.refreshTheater);
			d.okayButton.connect(gui.CLICK, continueAnyway)
			d.open();
		else:
			dialog.close()
			self.exportActual(fancy, amount, location)
	
	def exportActual(self, fancy, amount, location):
		self.script.refreshTheater()
		if location == "Here":
			if fancy == "Fancy":
				valueType = ['.html']
			else:
				valueType = ['.txt']
			exportName = filenameStrip(self.script.metadata.title) + valueType[0]
			d = gui.FileDialog(_("Export as %s") % fancy,
							   _("Okay"), 
							   path=directories['export-folder'], 
							   filter=valueType,
							   default = exportName,
							   favorites = defaults['favorites'])
			d.open()
			d.connect(gui.CLOSE, self.script.refreshTheater);
			d.connect(gui.CHANGE, self.exportFile, fancy, amount, d);
		else:
			teachers = getTeacherList()
			if teachers:
				d = gui.TeacherDialog()
				d.loadTeachers(teachers)
				d.connect(gui.CLOSE, self.script.refreshTheater);
				d.connect(gui.CHANGE, self.upload, fancy, amount, d);
				d.open()
			else:
				d= gui.ConfirmDialog(_("Connection Error"), [_("You are not connected to the internet."),
															 _("Connect and then click Okay below.")])
				def tryAgain():
					d.close()
					self.exportActual(fancy, amount, location)
				d.connect(gui.CLOSE, self.script.refreshTheater);
				d.okayButton.connect(gui.CLICK, tryAgain)
				d.open();
	
	def upload(self, _widget, fancy, amount, dialog):
		teacher = _widget.value
		try:
			dialog.close()
		except: pass
		try:
			self.script.saveFile(directories['temp']+"temp.bdw")
		except Exception, e:
			print "Failed to save bdw file.", e
		try:
			if fancy == "Fancy":
				self.script.export((directories['temp']+"tempExport", fancy, amount))
			elif fancy == "Plain":
				self.script.export((directories['temp']+"tempExport", fancy, amount))
		except Exception, e:
			print "Failed to export file.", e
		try:
			success= uploadToTeacher(teacher, self.script.metadata.title, fancy, directories['temp']+"temp.bdw", directories['temp']+"tempExport")
		except Exception, e:
			print "Failed to upload file.", e
			d= gui.ConfirmDialog(_("Upload Error"), [_("There was a problem uploading the script."),
														 _("Do you want to try again?")])
			def tryAgain():
				d.close()
				self.upload(_widget, fancy, amount, d)
			d.connect(gui.CLOSE, self.script.refreshTheater);
			d.okayButton.connect(gui.CLICK, tryAgain)
			d.open();
		
	def exportFile(self, _widget, fancy, amount, dialog):
		fullPath= _widget.value;
		fileName, fileExtension= os.path.splitext(fullPath);
		dialog.close()
		if fancy == "Fancy" and fileExtension != ".html":
			fullPath+= ".html"
		elif fancy == "Plain" and fileExtension != ".txt":
			fullPath+= ".txt"
		if os.path.isfile(fullPath):
			self.confirmActionDialog(_("Overwrite?"),
									[ _("This file already exists:"),
									  os.path.basename(fullPath),
									  _("Are you sure you want to overwrite it?")],
									okayFunction= self.script.export, 
									arguments=(fullPath,fancy, amount));
		else:
			self.script.export((fullPath, fancy, amount));
	
	def modifyScriptMetadata(self, property, _widget):
		#HACK: I'm sick of writing a different function for each property.
		setattr(self.script.metadata,property,_widget.value);
		self.script.scriptChanged();
		self.script.controls["file-button-save"].disabled= not self.script.unsaved;
		self.script.controls["file-button-save"].repaint();
	
	def changeLanguage(self):
		newLanguage= self.script.controls["file-button-language"].value
		global language
		language= newLanguage
		changeLanguage(newLanguage, languageCodes[languages.index(language)])
		sourceTab = self.sourceTab
		#sourceTab.changePanel()
		sourceTab.reload()
	
	def openNewDialog(self):
		self.newFile();
	def openLoadDialog(self):
		if self.script.filepath:
			loadName = os.path.basename(self.script.filepath)
		else:
			loadName = ""
		d = gui.FileDialog(_("Open a script"),
						   _("Okay"), 
						   path=directories['sample-scripts'], 
						   filter=[information['filetype']],
						   default= loadName,
						   favorites = defaults['favorites'])
		d.open()
		d.connect(gui.CLOSE, self.script.refreshTheater);
		d.connect(gui.CHANGE, self.loadFile);
	def openSaveDialog(self):
		if self.script.filepath is not None:
			self.script.saveFile(self.script.filepath);
			self.script.controls["file-button-save"].disabled= not self.script.unsaved;
			self.script.controls["file-button-save"].blur();
			self.script.controls["file-button-save"].repaint();
		else:
			self.openSaveAsDialog();
	
	def openSaveAsDialog(self):
		if self.script.filepath:
			saveName = os.path.basename(self.script.filepath)
		else:
			saveName = filenameStrip(self.script.metadata.title) + information['filetype']
		d = gui.FileDialog(_("Save a script"),
						   _("Okay"), 
						   path=directories['export-folder'], 
						   filter=[information['filetype']],
						   default= saveName,
						   favorites = defaults['favorites'])
		d.open()
		d.connect(gui.CLOSE, self.script.refreshTheater);
		d.connect(gui.CHANGE, self.saveFile);
	
	
	def confirmActionDialog(self, title, message, okayFunction=None, cancelFunction=None, arguments= None):
		d= gui.ConfirmDialog(title, message)
		d.connect(gui.CLOSE, self.script.refreshTheater);
		if okayFunction is not None: 
			def okayAndCloseFunction(arguments):
				okayFunction(arguments);
				d.close();
				self.script.controls["file-button-save"].disabled= not self.script.unsaved;
				self.script.controls["file-button-save"].repaint();
				self.refreshPanel();
			d.okayButton.connect(gui.CLICK, okayAndCloseFunction, arguments);
		else:
			d.okayButton.connect(gui.CLICK, d.close);
		if cancelFunction is not None: 
			def cancelAndCloseFunction(arguments):
				cancelFunction(arguments);
				d.close();
				self.script.controls["file-button-save"].disabled= not self.script.unsaved;
				self.script.controls["file-button-save"].repaint();
				self.refreshPanel();
			d.cancelButton.connect(gui.CLICK, cancelAndCloseFunction, arguments);
		else:
			d.cancelButton.connect(gui.CLICK, d.close);
		d.open()
	
	def saveFile(self, _widget):
		fullPath= _widget.value;
		fileName, fileExtension= os.path.splitext(fullPath);
		if fileExtension != information['filetype']:
			fullPath+= information['filetype'];
		if os.path.isfile(fullPath):
			self.confirmActionDialog(_("Overwrite?"),
									[ _("This file already exists:"),
									  os.path.basename(fullPath),
									  _("Are you sure you want to overwrite it?")],
									okayFunction= self.script.saveFile, 
									arguments=fullPath);
		else:
			self.script.saveFile(fullPath);
	
	def loadFile(self, _widget):
		fullPath= _widget.value;
		if self.script.unsaved:
			self.confirmActionDialog(_("Lose Unsaved Changes?"),
									[ _("You have unsaved changes!"),
									  _("Are you sure you want to load a  script?")],
									okayFunction= self.script.loadFile, 
									arguments=fullPath);
		else:
			self.script.loadFile(fullPath);
			self.refreshPanel();
	
	def newFile(self):
		if self.script.unsaved:
			self.confirmActionDialog(_("Lose Unsaved Changes?"),
									[ _("You have unsaved changes!"),
									  _("Are you sure you want to start a new script?")],
									okayFunction= self.script.newFile);
		else:
			self.script.default();
			self.refreshPanel();

class BackdropPanel(Panel):
	# Choose a backdrop
	name= "Backdrop";
	def __init__(self, script):
		Panel.__init__(self);
		self.script= script;
		
		self.groups= None;
		self.backdropIndex= 0;
		self.backdropsOnscreen= min(5, len(backdrops));
	
	def gotoBackdropPage(self, to):
		#self.tearDown();
		self.groups= None;
		self.owningWidgets= [];
		self.clear();
		#checkAllWidgets(self, self);
		to= min(to, len(backdrops)-self.backdropsOnscreen);
		to= max(to, 0);
		self.backdropIndex= to;
		self.build();
			
	
	def build(self):
		Panel.build(self);
		backdropDocument= gui.Document(width=geom['panel'].width, align=0);
		back= self.script.backdrop;
		
		backdropGroup= gui.Group('backdrop-group-backdrops', back);
		backdropGroup.connect(gui.CHANGE, self.changeBackdrop);	
		
		start= self.backdropIndex;
		end= min(len(backdrops), self.backdropIndex + self.backdropsOnscreen);
		
		for aBackdrop in backdrops[start:end]:
			thumbPath= os.path.join('games/broadway/backdrops',aBackdrop+'_thumb.png');
			filePath= aBackdrop;
			backdropToolTable= gui.Table();
			backdropToolTable.tr();
			backdropToolTable.td(gui.Image(thumbPath));
			backdropToolTable.tr();
			backdropToolTable.td(gui.Label(translate(string.capwords(aBackdrop))));
			backdropTool= gui.Tool(backdropGroup, 
								backdropToolTable, 
								filePath,
								style={'margin':4},
								name='backdrop-tool-backdrops-'+aBackdrop);
			backdropDocument.add(backdropTool);
			backdropDocument.add(gui.Spacer(4,6));
		
		#Custom Backdrop from local source
		customBackdropButton = gui.Button(_("Your's"),
									  name='backdrop-button-backdrops-custom', 
									  style={'width': 80, 'height': 32})
		customBackdropButton.connect(gui.CLICK, self.externalBackdrop)
		
		#Custom Backdrop from online source (teacher)
		teacherBackdropButton = gui.Button(_("Teacher's"),
										name='backdrop-button-backdrops-teacher', 
										style={'width': 80, 'height': 32})
		teacherBackdropButton.connect(gui.CLICK, self.teacherBackdrop)
		
		backdropGroup.connect(gui.CHANGE, self.changeBackdrop)
		self.groups= backdropGroup
		
		navigationButtons= gui.Table(width=geom['panel'].width);
		navigationButtons.tr();
		maxSize= (len(backdrops) - self.backdropsOnscreen - 1);
		size= geom['panel'].width * 3/4 / (1+ (maxSize / float(self.backdropsOnscreen)));
		progressBar= gui.HSlider(value= self.backdropIndex,
								 min= 0,
								 max= maxSize,
								 size= size,
								 step= 1,
								 disabled= True,
								 width= geom['panel'].width * 3/4,
								 style= {'padding': 4,
										 'margin' : 10});
		navigationButtons.td(progressBar, colspan= 5);
		navigationButtons.tr();
		homeButton= gui.Button(gui.Image(images['go-first']));
		homeButton.connect(gui.CLICK, self.gotoBackdropPage, 0);
		navigationButtons.td(homeButton);
		previousButton= gui.Button(gui.Image(images['go-back']));
		previousButton.connect(gui.CLICK, self.gotoBackdropPage, self.backdropIndex-self.backdropsOnscreen);
		navigationButtons.td(previousButton);
		if start == end:
			label= _("No backdrops loaded");
		elif (end - start) == 1:
			label= _("Backdrop %d") % (start+1);
		else:
			label= _("Backdrops %d to %d") % (start+1, end);
		navigationButtons.td(gui.Label(label));
		forwardButton= gui.Button(gui.Image(images['go-next']));
		forwardButton.connect(gui.CLICK, self.gotoBackdropPage, self.backdropIndex+self.backdropsOnscreen);
		navigationButtons.td(forwardButton);
		endButton= gui.Button(gui.Image(images['go-last']));
		endButton.connect(gui.CLICK, self.gotoBackdropPage, len(backdrops));
		navigationButtons.td(endButton);
			
		self.add(backdropDocument, 0, 30);
		self.add(navigationButtons, 0, geom['panel'].height // 2 + 25);
		self.add(customBackdropButton, 10, 50)
		self.add(teacherBackdropButton, 10, 100)
		self.owningWidgets.append(customBackdropButton)
		self.owningWidgets.append(teacherBackdropButton)
		self.owningWidgets.append(backdropDocument);
		self.owningWidgets.append(navigationButtons);
	
	def changeBackdrop(self):
		back= self.script.controls['backdrop-group-backdrops'].value;
		self.script.setBackdrop(backdrop.Backdrop(back));
		self.script.scriptChanged();
	
	def externalBackdrop(self):
		d = gui.FileDialog(_("Load a Picture"),
						   _("Okay"), 
						   path=directories['images'], 
						   filter=['.png','.bmp','.jpg','.jpeg','.gif'],
						   favorites = defaults['favorites'])
		d.open()
		d.connect(gui.CLOSE, self.script.refreshTheater);
		d.connect(gui.CHANGE, self.loadBackdrop);
	
	def teacherBackdrop(self):
		teachers = getTeacherList()
		if teachers:
			d = gui.TeacherDialog()
			d.loadTeachers(teachers)
			d.connect(gui.CLOSE, self.script.refreshTheater);
			d.connect(gui.CHANGE, self.loadTeacherBackdrop);
			d.open()
		else:
			d= gui.ConfirmDialog(_("Connection Error"), [_("You are not connected to the internet."),
														 _("Connect and then click Okay below.")])
			def tryAgain():
				d.close()
				self.teacherBackdrop()
			d.connect(gui.CLOSE, self.script.refreshTheater);
			d.okayButton.connect(gui.CLICK, tryAgain)
			d.open();
			
	def loadTeacherBackdrop(self, _widget):
		username= _widget.value
		try:
			downloadTeachersImage(username)
		except Exception, e:
			print "Could not connect.",e
			d= gui.ConfirmDialog(_("Connection Error"), [_("You are not connected to the internet."),
														 _("Connect and then click Okay below.")])
			def tryAgain():
				d.close()
				self.teacherBackdrop()
			d.connect(gui.CLOSE, self.script.refreshTheater);
			d.okayButton.connect(gui.CLICK, tryAgain)
			d.open();
			
		self.script.setBackdrop(backdrop.Backdrop(images['teacher-backdrop'], external=True));
		self.script.scriptChanged();
		
		#exportOptions = gui.Document()
		#exportButtons= [(gui.Button(_("Text"), name= 'file-button-export-text', style={'margin':4}), 'text', ['.txt']),
						#(gui.Button(_("HTML"), name= 'file-button-export-html', style={'margin':4}), 'html', ['.html'])]
		#, (gui.Button(_("Video"), name= 'file-button-export-text', style={'margin':4}), 'video', ['.mpeg'])
		# d= gui.Dialog(gui.Label(_("Export")), exportOptions)
		# for aButton, value, valueType in exportButtons:
			# exportOptions.add(aButton)
			# aButton.connect(gui.CLICK, self.export, value, valueType, d)
		# d.connect(gui.CLOSE, self.script.refreshTheater);
		# d.open()

	def loadBackdrop(self, _widget):
		fullPath= _widget.value;
		self.script.setBackdrop(backdrop.Backdrop(fullPath, external=True));
		self.script.scriptChanged();
		#for x in getAllInstances(backdrop.Backdrop):
			#checkBackrefs(x,str(id(x)),[self]);

class ActorPanel(Panel):
	# Add/remove/modify actors
	# change name, voice, costume, pose, look, position, direction
	name= "Actor";
	def __init__(self, script):
		Panel.__init__(self);
		self.script= script;
		self.waitingOnMouse= False;
	
	def build(self):
		Panel.build(self);
		self.groups= [];
		self.editablesDocumentLeft= None;
		self.editablesDocumentRight= None;
		self.focusDocument= None;
		self.buildFocusSelecter();
		minusButton= gui.Button(_("Remove Actor"), name='actor-button-remove', style={'margin':10, 'padding':5});
		minusButton.connect(gui.CLICK, self.removeActor);
		self.add(minusButton, geom['panel'].width - minusButton.getWidth(), 20);
		self.owningWidgets.append(minusButton);
	
	def changeFocus(self, value= None):
		if value == None:
			value= self.script.controls['actor-group-focus'].value;
		else:
			self.script.controls['actor-group-focus'].value= value;
		if value == _("Add actor"):
			self.addActor();
		else:
			self.killEditableDocument();
			self.buildEditablesDocument();
	
	def addActor(self):
		newActor= actor.Actor(defaults['actor'],defaults['actorName']);
		self.script.addActor(newActor);
		newActor.state.position= defaults['positions'][len(self.script.actors)-2];
		newActor.changeBodyPosition();
		self.buildFocusSelecter(newActor);
		self.script.scriptChanged();
	
	def removeActor(self):
		newActor= self.script.controls['actor-group-focus'].value;
		if newActor != self.script.actors[0]:
			self.script.controls['actor-group-focus'].value= self.script.actors[0];
			positionInList= self.script.actors.index(newActor);
			self.script.controls['actor-tool-focus-'+str(positionInList)].value= None;
			self.script.controls['actor-button-test'].disconnect(gui.CLICK);
			self.script.removeActor(newActor);
			self.buildFocusSelecter();
			self.script.scriptChanged();
	
	def killEditableDocument(self):
		self.editablesDocumentLeft.kill();
		self.remove(self.editablesDocumentLeft);
		if self.editablesDocumentLeft in self.owningWidgets:
			self.owningWidgets.remove(self.editablesDocumentLeft);
		self.editablesDocumentRight.kill();
		self.remove(self.editablesDocumentRight);
		if self.editablesDocumentRight in self.owningWidgets:
			self.owningWidgets.remove(self.editablesDocumentRight);
	
	def buildEditablesDocument(self):
		newActor= self.script.controls['actor-group-focus'].value;
		self.editablesDocumentLeft= gui.Document();
		self.editablesDocumentRight= gui.Document();
		self.add(self.editablesDocumentLeft,10,95);
		self.add(self.editablesDocumentRight,510,95);
		if newActor != self.script.actors[0]:
			self.buildNameInput();
			self.buildSkinSelecter();
		self.buildVoiceSelecter();
		if newActor != self.script.actors[0]:
			self.buildLookSelecter();
			self.buildPoseSelecter();
			self.buildDirectionSelecter();
			self.buildMovers();
		self.owningWidgets.append(self.editablesDocumentLeft);
		self.owningWidgets.append(self.editablesDocumentRight);
	
	####################################
	
	def buildPoseSelecter(self):
		focusedActor= self.script.controls['actor-group-focus'].value;
		poses= focusedActor.poses;
		pose= self.script.frames[0][focusedActor].pose;
		
		poseSelecter= gui.Select(name='actor-select-pose', value=pose, cols=3);
		poseSelecter.connect(gui.SELECT, self.changePose);
		for aPose in poses:
			prettyPose= aPose.replace('_',' ').title();
			poseSelecter.add(translate(prettyPose), aPose);
		
		self.editablesDocumentRight.add(gui.Label(_("Initial Pose: ")));
		self.editablesDocumentRight.add(poseSelecter);
		self.spaceEditablesDocumentRight();
	
	def changePose(self):
		pose= self.script.controls['actor-select-pose'].value;
		focusedActor= self.script.controls['actor-group-focus'].value;
		doAction= action.Action(focusedActor,
								  verbs.DO,
								  pose);
		self.script.applyAction(0,doAction);
		focusedActor.state.pose= pose;
		focusedActor.changeBodyPose();
		self.script.scriptChanged();
		
	def changeLook(self):
		look= self.script.controls['actor-select-look'].value;
		focusedActor= self.script.controls['actor-group-focus'].value;
		feelAction= action.Action(focusedActor,
								  verbs.FEEL,
								  look);
		self.script.applyAction(0,feelAction);
		focusedActor.state.look= look;
		focusedActor.changeFaceExpression();
		self.script.scriptChanged();
	
	#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
	
	def buildLookSelecter(self):
		focusedActor= self.script.controls['actor-group-focus'].value;
		looks= focusedActor.looks;
		look= self.script.frames[0][focusedActor].look;
		
		lookSelecter= gui.Select(name='actor-select-look', value=look, cols=4);
		lookSelecter.connect(gui.SELECT, self.changeLook);
		for aLook in looks:
			prettyLook= translate(aLook.replace('_',' ').title());
			lookSelecter.add(prettyLook, aLook);
		
		self.editablesDocumentRight.add(gui.Label(_("Initial Look: ")));
		self.editablesDocumentRight.add(lookSelecter);
		self.spaceEditablesDocumentRight();
	
	def buildDirectionSelecter(self):
		focusedActor= self.script.controls['actor-group-focus'].value;
		direction= self.script.frames[0][focusedActor].direction;
		
		self.editablesDocumentRight.add(gui.Label(_("Initial Face: ")));
		for aDirection in directions:
			prettyDirection= aDirection.replace('_',' ').title();
			positionButton= gui.Button(translate(prettyDirection), name='actor-button-direction-'+prettyDirection);
			positionButton.connect(gui.CLICK, self.changeDirection, aDirection);
			self.editablesDocumentRight.add(positionButton);
		self.spaceEditablesDocumentRight();
	
	def changeDirection(self, direction):
		focusedActor= self.script.controls['actor-group-focus'].value;
		faceAction= action.Action(focusedActor,
								  verbs.FACE,
								  direction);
		self.script.applyAction(0,faceAction);
		focusedActor.state.direction= direction;
		focusedActor.changeBodyDirection();
		self.script.scriptChanged();
		
	####################################
	
	def buildMovers(self):
		focusedActor= self.script.controls['actor-group-focus'].value;
		position= self.script.frames[0][focusedActor].position;
		offscreen= type(position) is str;
		
		positionButton= gui.Button(_("Move"), name='actor-button-move');
		positionButton.connect(gui.CLICK, self.changePositionAbsolutely);
		self.editablesDocumentRight.add(positionButton);
		
		self.editablesDocumentRight.add(gui.Label(_(" or start offscreen ")));
		
		positionSwitch= gui.Switch(value=offscreen, name='actor-switch-offscreen');
		positionSwitch.connect(gui.CLICK, self.changePosition);
		self.editablesDocumentRight.add(positionSwitch);
		self.spaceEditablesDocumentRight();
	
	def changePositionAbsolutely(self):
		pygame.mouse.set_cursor(*pygame.cursors.broken_x);
		self.waitingOnMouse= True;
		self.script.scriptChanged();
	
	def changePosition(self):
		offscreen= self.script.controls['actor-switch-offscreen'].value;
		if offscreen:
			position= defaults['position'];
		else:
			position= 'left';
		focusedActor= self.script.controls['actor-group-focus'].value;
		moveAction= action.Action(focusedActor,
								  verbs.MOVE,
								  position);
		self.script.applyAction(0,moveAction);
		focusedActor.state.position= position;
		focusedActor.changeBodyPosition();
		self.script.scriptChanged();
	
	def handleGlobalMouse(self, position, button):
		if self.waitingOnMouse:
			pygame.mouse.set_cursor(*pygame.cursors.arrow);
			if button == 1:
				focusedActor= self.script.controls['actor-group-focus'].value;
				moveAction= action.Action(focusedActor,
										  verbs.MOVE,
										  position);
				self.script.applyAction(0,moveAction);
				focusedActor.state.position= position;
				focusedActor.changeBodyPosition();
				self.script.controls['actor-switch-offscreen'].value= False;
			self.waitingOnMouse= False;
		else:
			newFocus= None;
			for anActor in self.script.actors:
				#print anActor.rect, position;
				if anActor.rect.collidepoint(position) and button == 1:
					newFocus= anActor;
			if newFocus is not None:
				self.script.controls['actor-group-focus'].change(newFocus);
				self.killEditableDocument();
				self.buildEditablesDocument();
	
	def buildSkinSelecter(self):
		newActor= self.script.controls['actor-group-focus'].value;
		skinSelecter= gui.Select(name='actor-select-skin', value=newActor.directory, cols=4);
		skinSelecter.connect(gui.SELECT, self.changeSkin);
		for aSkin in actors:
			if aSkin != "narrator":
				prettyActor= translate(aSkin.replace('_',' ').title());
				skinSelecter.add(prettyActor, aSkin);
		self.editablesDocumentLeft.add(gui.Label(_("Actor: ")));
		self.editablesDocumentLeft.add(skinSelecter);
		self.spaceEditablesDocumentLeft();
	
	def changeSkin(self):
		currentActor= self.script.controls['actor-group-focus'].value;
		currentActor.changeImages(self.script.controls['actor-select-skin'].value);
		self.script.controls['actor-select-skin']._close(None);
		self.buildFocusSelecter(currentActor);
		self.script.scriptChanged();
	
	def buildNameInput(self):
		newActor= self.script.controls['actor-group-focus'].value;
		nameInput= gui.Input(name='actor-input-name', value=newActor.name,size=30);
		nameInput.connect(gui.BLUR, self.changeName);
		self.editablesDocumentLeft.add(gui.Label(_("Name: ")));
		self.editablesDocumentLeft.add(nameInput);
		self.spaceEditablesDocumentLeft();
	
	def changeName(self):
		currentActor= self.script.controls['actor-group-focus'].value;
		currentActor.name= self.script.controls['actor-input-name'].value;
		self.buildFocusSelecter(currentActor);
		self.script.scriptChanged();
	
	def buildVoiceSelecter(self):
		newActor= self.script.controls['actor-group-focus'].value;
		voiceSelecter= gui.Select(name='actor-select-voice', value=newActor.voice, cols=8);
		voiceSelecter.connect(gui.SELECT, self.changeVoice);
		for aVoice in voices:
			voiceSelecter.add(translate(aVoice.visibleName), aVoice);
		self.editablesDocumentLeft.add(gui.Label(_("Voice: ")));
		self.editablesDocumentLeft.add(voiceSelecter);
		speakButton= gui.Button(_("Test"), name='actor-button-test');
		speakButton.connectWeakly(gui.CLICK, newActor.quickSpeak, defaults['voice-test']);
		self.editablesDocumentLeft.space((10,1));
		self.editablesDocumentLeft.add(speakButton);
		self.spaceEditablesDocumentLeft();
	
	def changeVoice(self):
		newActor= self.script.controls['actor-group-focus'].value;
		newVoice= self.script.controls['actor-select-voice'].value;
		newActor.voice= newVoice;
		self.script.scriptChanged();
	
	def spaceEditablesDocumentLeft(self):
		self.editablesDocumentLeft.br(1);
		self.editablesDocumentLeft.add(gui.Spacer(4,5));
		self.editablesDocumentLeft.br(1);
	def spaceEditablesDocumentRight(self):
		self.editablesDocumentRight.br(1);
		self.editablesDocumentRight.add(gui.Spacer(4,5));
		self.editablesDocumentRight.br(1);
	
	def buildFocusSelecter(self, focus=None):
		if self.focusDocument is not None:
			self.groups= [];
			self.focusDocument.clear();
			self.remove(self.focusDocument);
			if self.focusDocument in self.owningWidgets:
				self.owningWidgets.remove(self.focusDocument);
			self.killEditableDocument();
			
		actors= self.script.actors;
		if focus is not None:
			focusGroup= gui.Group('actor-group-focus', focus);
		else:
			focusGroup= gui.Group('actor-group-focus', actors[0]);
		focusGroup.connect(gui.CHANGE, self.changeFocus);
		self.groups.append(focusGroup);

		focusDocument= gui.Document();
		length= 20-len(actors);
		i= 0;
		for anActor in actors:
			focusToolTable= gui.Table();
			focusToolTable.tr();
			focusToolTable.td(gui.Image(anActor.thumb));
			focusToolTable.tr();
			focusToolTable.td(gui.Label(anActor.shortName(length)));
			focusTool= gui.Tool(focusGroup, 
								focusToolTable, 
								anActor,
								name='actor-tool-focus-'+str(i));
			focusDocument.add(focusTool);
			focusDocument.add(gui.Spacer(4,1));
			i+= 1;
		if len(actors) < limits['actors']:
			plusLabel= gui.Label(_("Add actor"));
			plusTool= gui.Tool(focusGroup, 
								plusLabel, 
								_("Add actor"),
								style={'margin':10, 'padding':5},
								name= 'actor-focus-plusTool');
			focusDocument.add(plusTool);
		self.add(focusDocument, 20,20);
		self.focusDocument= focusDocument;
		self.buildEditablesDocument();
		self.owningWidgets.append(focusDocument);

class PlanPanel(Panel):
	# Story title, theme, conflict, 
	# Probably not going to be included in this version, but maybe in the next
	# one.
	name= "Plan";
	def __init__(self):
		Panel.__init__(self);
	
class WritePanel(Panel):
	# Write story, change character, pose, look, position, direction
	name= "Write";
	def __init__(self, script):
		Panel.__init__(self);
		self.script= script;
		self.scriptArea= ScriptArea(self.script, 
									width= geom['scriptArea'].width, 
									height= geom['scriptArea'].height,
									name='write-scriptArea-script');		
		self.selectablesDocumentTable= None;
		self.focusDocument= None;
		self.waitingOnMouse= False;
	
	def build(self):
		Panel.build(self);
		self.groups= [];
		self.plotTwist= self.script.getRandomTwist();
		self.add(self.scriptArea, *geom['scriptArea'].topleft);
		self.scriptArea.refreshScript();
		self.script.director.reset();
		self.on= True;
		self.playButton= gui.Button(_("Test"), name='write-button-test');
		self.playButton.connect(gui.CLICK, self.playHighlighted);
		self.add(self.playButton, geom['panel'].width-60, geom['scriptPanel'].top+15);
		self.buildFocusSelecter();
	
	def tearDown(self):
		Panel.kill(self);
		self.groups= [];
	
	def stopHighlighted(self):
		self.playButton.value= _("Test");
		self.on= True;
		self.script.enableControls();
		
	def playHighlighted(self):
		if self.on:
			self.playButton.value= _("Stop");
			start, end= self.scriptArea.getSelectedTime();
			if start == end:
				self.script.director.startAt(start, callback= self.stopHighlighted);
			else: 
				self.script.director.startRange(start, end, callback= self.stopHighlighted);
			self.script.disableControls(['write-button-test']);
			self.on= False;
		else:
			self.stopHighlighted();
			self.script.director.stop();
	
	def buildPoseSelecter(self):
		actor= self.script.controls['write-group-focus'].value;
		poses= actor.poses;
		pose= actor.state.pose;
		
		poseSelecter= gui.Select(name='write-select-pose', value=pose, cols=3);
		poseSelecter.connect(gui.SELECT, self.changePose);
		for aPose in poses:
			prettyPose= translate(aPose.replace('_',' ').title());
			poseSelecter.add(prettyPose, aPose);
		
		self.selectablesDocumentLeft.add(gui.Label(_("Change Pose: ")));
		self.selectablesDocumentLeft.add(poseSelecter);
		self.spaceSelectableDocumentLeft();
		
	def changeLook(self):
		newLook= self.script.controls['write-select-look'].value;
		self.scriptArea.insertCue(verbs.FEEL, newLook);
		self.scriptArea.insertLetter(' ');
		self.scriptArea.moveRight();
		self.scriptArea.focus();
		self.script.scriptChanged();
	
	def buildLookSelecter(self):
		actor= self.script.controls['write-group-focus'].value;
		looks= actor.looks;
		look= actor.state.look;
		
		lookSelecter= gui.Select(name='write-select-look', value=look, cols=4);
		lookSelecter.connect(gui.SELECT, self.changeLook);
		for aLook in looks:
			prettyLook= translate(aLook.replace('_',' ').title())
			lookSelecter.add(prettyLook, aLook);
		
		self.selectablesDocumentLeft.add(gui.Label(_("Look: ")));
		self.selectablesDocumentLeft.add(lookSelecter);
		self.spaceSelectableDocumentLeft();
		
	def changePose(self):
		newPose= self.script.controls['write-select-pose'].value;
		self.scriptArea.insertCue(verbs.DO, newPose);
		self.scriptArea.insertLetter(' ');
		self.scriptArea.moveRight();
		self.scriptArea.focus();
		self.script.scriptChanged();
	
	def buildDirectionSelecter(self):
		actor= self.script.controls['write-group-focus'].value;
		direction= actor.state.direction;

		self.selectablesDocumentRight.add(gui.Label(_("Face: ")));
		for aDirection in directions:
			prettyDirection= aDirection.replace('_',' ').title();
			positionButton= gui.Button(translate(prettyDirection), name='write-button-direction-'+prettyDirection);
			positionButton.connect(gui.CLICK, self.changeDirection, aDirection);
			self.selectablesDocumentRight.add(positionButton);
		self.spaceSelectableDocumentRight();
	
	def changeDirection(self, direction):
		self.scriptArea.insertCue(verbs.FACE, direction);
		#HACK: Insert a space to keep from breaking lines stupidly
		self.scriptArea.insertLetter(' ');
		self.scriptArea.moveRight();
		self.scriptArea.focus();
		self.script.scriptChanged();
	
	def buildIdeaGenerator(self):
		ideaButton= gui.Button(_("New Idea"), name='write-button-newTwist');
		ideaButton.connect(gui.CLICK, self.generateNewIdea);
		self.selectablesDocumentLeft.add(ideaButton);
		
		self.selectablesDocumentLeft.add(gui.Spacer(20,5));
		
		useButton= gui.Button(_("Use Idea"), name='write-button-useTwist');
		useButton.connect(gui.CLICK, self.useIdea);
		self.selectablesDocumentLeft.add(useButton);
		
		self.spaceSelectableDocumentLeft();
		
		self.selectablesDocumentTable.tr();
		
		self.selectablesDocumentTable.td(gui.Label(value=_("Current Idea:")));
		self.selectablesDocumentTable.tr();
		
		longestPlotTwist= self.script.getLongestTwist();
		ideaLabel= gui.WidthLabel(value=longestPlotTwist,
							 width= geom['scriptPanel'].width,
							 name='write-label-twist');
		self.selectablesDocumentTable.td(ideaLabel);
		ideaLabel.value= self.plotTwist;
	
	def generateNewIdea(self, _widget):
		self.plotTwist= self.script.getRandomTwist();
		self.script.controls['write-label-twist'].value= self.plotTwist;
		
	def useIdea(self):
		plotTwistText= self.script.controls['write-label-twist'].value;
		self.script.disableControls();
		self.scriptArea.insertString(plotTwistText);
		self.script.enableControls();
		self.scriptArea.focus();
		self.script.scriptChanged();
	
	def buildMovers(self):
		actor= self.script.controls['write-group-focus'].value;
		position= actor.state.position;
	
		self.selectablesDocumentRight.add(gui.Label(value=getMoveString(position),
												name='write-label-position'));
		for aDirection in directions:
			prettyDirection= aDirection.replace('_',' ').title();
			positionButton= gui.Button(translate(prettyDirection), name='write-button-direction-'+prettyDirection);
			positionButton.connect(gui.CLICK, self.changePosition, aDirection);
			self.selectablesDocumentRight.add(positionButton);
		self.spaceSelectableDocumentRight();
		
		positionButton= gui.Button(_("Move"), name='write-button-move');
		positionButton.connect(gui.CLICK, self.changePositionAbsolutely);
		self.selectablesDocumentRight.add(positionButton);
		self.spaceSelectableDocumentRight();
	
	def spaceSelectableDocumentRight(self):
		self.selectablesDocumentRight.br(1);
		self.selectablesDocumentRight.add(gui.Spacer(4,15));
		self.selectablesDocumentRight.br(1);
	def spaceSelectableDocumentLeft(self):
		self.selectablesDocumentLeft.br(1);
		self.selectablesDocumentLeft.add(gui.Spacer(4,15));
		self.selectablesDocumentLeft.br(1);
	
	def changePositionAbsolutely(self):
		pygame.mouse.set_cursor(*pygame.cursors.broken_x);
		self.waitingOnMouse= True;
	
	def handleGlobalMouse(self, position, button):
		if self.waitingOnMouse:
			pygame.mouse.set_cursor(*pygame.cursors.arrow);
			if geom['theater'].collidepoint(position) and button == 1:
				self.scriptArea.insertCue(verbs.MOVE, position);
				self.scriptArea.insertLetter(' ');
				self.scriptArea.moveRight();
				self.scriptArea.focus();
				self.script.scriptChanged();
			self.waitingOnMouse= False;
		else:
			newFocus= None;
			for anActor in self.script.actors:
				if anActor.rect.collidepoint(position) and button == 1:
					newFocus= anActor;
			if newFocus is not None:
				self.script.controls['write-group-focus'].change(newFocus);
				self.scriptArea.changeActor(newFocus);
				self.killSelectablesDocument();
				self.buildSelectablesDocument();
				self.scriptArea.focus();
	
	def changePosition(self, direction):
		actor= self.script.controls['write-group-focus'].value;
		position= actor.state.position;
		if type(position) is str:
			self.scriptArea.insertCue(verbs.ENTER, 
									  self.getMovePosition(direction));
		else:
			self.scriptArea.insertCue(verbs.EXIT, direction);
		self.scriptArea.insertLetter(' ');
		self.scriptArea.moveRight();
		self.scriptArea.focus();
		self.script.scriptChanged();
	
	def getMovePosition(self, direction):
		if direction == 'left':
			return marks['houseLeft'];
		else:
			return marks['houseRight'];
	
	def buildFocusSelecter(self):
		if self.focusDocument in self.widgets:
			self.groups= [];
			self.focusDocument.clear();
			self.remove(self.focusDocument);
			if self.focusDocument in self.owningWidgets:
				self.owningWidgets.remove(self.focusDocument);
			self.killSelectablesDocument();
			self.remove(self.focusDocument);
		actors= self.script.actors;
		focusGroup= gui.Group('write-group-focus', self.script.getFirstActor());
		focusGroup.connect(gui.CHANGE, self.changeFocus);
		self.groups.append(focusGroup);
		
		focusDocument= gui.Document();
		focusDocument.add(gui.Label(_("Change speaker:")));
		focusDocument.br(1);
		length= 15-len(actors);
		for anActor in actors:
			focusToolTable= gui.Table();
			focusToolTable.tr();
			focusToolTable.td(gui.Image(anActor.thumb));
			focusToolTable.tr();
			focusToolTable.td(gui.Label(anActor.shortName(length)));
			focusTool= gui.Tool(focusGroup, 
								focusToolTable, 
								anActor,
								name='write-tool-focus-'+anActor.name);
			focusDocument.add(focusTool);
			focusDocument.add(gui.Spacer(4,1));
					
		self.add(focusDocument, *geom['scriptPanel'].topleft);
		
		self.focusDocument= focusDocument;
		self.buildSelectablesDocument();
	
	def changeFocus(self):
		newActor= self.script.controls['write-group-focus'].value;
		self.scriptArea.changeActor(newActor);
		self.killSelectablesDocument();
		self.buildSelectablesDocument();
		self.script.controls['panel-image-background'].repaint();
		self.script.scriptChanged();
	
	def killSelectablesDocument(self):
		self.selectablesDocumentTable.kill();
		self.remove(self.selectablesDocumentTable);
		if self.selectablesDocumentTable in self.widgets:
			self.owningWidgets.remove(self.selectablesDocumentTable);
	
	def buildSelectablesDocument(self):
		#self.script.disableControls();
		newActor= self.script.controls['write-group-focus'].value;
		self.selectablesDocumentTable= gui.Table(width= geom['scriptPanel'].width,
												 height= geom['scriptPanel'].height / 2);
		self.selectablesDocumentTable.tr();
		self.selectablesDocumentLeft= gui.Document(width= geom['scriptPanel'].width/2);
		self.selectablesDocumentTable.td(self.selectablesDocumentLeft);
		self.selectablesDocumentRight= gui.Document(width= geom['scriptPanel'].width/2);
		self.selectablesDocumentTable.td(self.selectablesDocumentRight);
		self.add(self.selectablesDocumentTable,
				geom['scriptPanel'].left,
				geom['scriptPanel'].top+ 75);
		if newActor == self.script.actors[0]:
			self.buildIdeaGenerator();
		else:
			self.buildLookSelecter();
			self.buildPoseSelecter();
			self.buildDirectionSelecter();
			self.buildMovers();
		#self.script.enableControls();
		self.scriptArea.focus();
	
class TheaterPanel(Panel):
	# Blank while playing
	name= "Theater";
	def __init__(self, script):
		Panel.__init__(self);
		self.script= script;
		self.director= self.script.director;
	
	def stopScript(self):
		self.playButton.value= gui.Image(images['media-play']);
		self.playButton.activated= False;
		self.script.enableControls();
		
	def playScript(self):
		if self.playButton.activated:
			self.stopScript();
			self.script.director.stop();
		else:
			self.playButton.value= gui.Image(images['media-pause']);
			self.playButton.activated= True;
			if self.script.director.isDone():
				self.script.director.reset();
				self.progressSlider.value= 0;
			position= self.progressSlider.value;
			self.script.director.startAt(position, 
										 callback= self.stopScript, 
										 continualCallback= self.updateProgressBar);
			self.script.disableControls(['write-button-test']);
			self.on= False;
	
	def buildProgressSliderArguments(self):
		initial= self.director.timeProgress;
		start= 0;
		end= len(self.script.actions);
		if end < 1: end= 1;
		width= geom['panel'].width / 2;
		height= 16;
		size= max(16, width / (1+end));
		return {'value' : initial,
				'min': start, 
				'max': end,
				'size': size, 
				'width': width, 
				'height': height,
				'style': {'padding': 4}};
	
	def updateProgressBar(self, timeProgress, actionProgress):
		self.progressSlider.value= timeProgress;
	
	def changeProgressBar(self):
		self.director.goto(self.progressSlider.value, None);

	def build(self):
		# Play Button
		# Pause Button
		# Rewind, Forward
		# Slider
		Panel.build(self);
		theaterTable= gui.Table(height= geom['panel'].height,
								width= geom['panel'].width * 3/4);
		theaterTable.tr();
		
		rewindAllButton= gui.Button(gui.Image(images['media-first']), style={'padding':5})
		rewindButton= gui.Button(gui.Image(images['media-backward']), style={'padding':5});
		self.playButton= gui.Button(gui.Image(images['media-play']), style={'padding':5});
		forwardButton= gui.Button(gui.Image(images['media-forward']), style={'padding':5});
		forwardAllButton= gui.Button(gui.Image(images['media-last']), style={'padding':5});
		
		self.script.director.reset();
		self.progressSlider= gui.HSlider(**self.buildProgressSliderArguments());
		self.progressSlider.connect(gui.CLICK, self.changeProgressBar);
		
		rewindAllButton.connect(gui.CLICK, self.director.rewindAll, self.updateProgressBar);
		rewindButton.connect(gui.CLICK, self.director.rewind, self.updateProgressBar);
		self.playButton.connect(gui.CLICK, self.playScript);
		forwardButton.connect(gui.CLICK, self.director.forward, self.updateProgressBar);
		forwardAllButton.connect(gui.CLICK, self.director.forwardAll, self.updateProgressBar);
		
		self.playButton.activated= False;

		theaterTable.td(gui.Spacer(1,1), align= 0);
		theaterTable.td(rewindAllButton, align= 0);
		theaterTable.td(rewindButton, align= 0);
		theaterTable.td(self.playButton, align= 0);
		theaterTable.td(forwardButton, align= 0);
		theaterTable.td(forwardAllButton, align= 0);
		theaterTable.td(gui.Spacer(1,1), align= 0);
		
		
		theaterTable.tr();
		theaterTable.td(self.progressSlider, colspan=7, align= 0);
		
		theaterTable.tr();
		theaterTable.td(gui.Label(_("Subtitles:  ")),
						colspan= 2, align=1);
		subtitleSwitch= gui.Switch(value=hacks['subtitle'], name='theater-switch-subtitles');
		subtitleSwitch.connect(gui.CLICK, self.subtitleSwitchState);
		theaterTable.td(subtitleSwitch, colspan= 1, align=-1);
		theaterTable.td(gui.Spacer(1,1), colspan= 1);
		theaterTable.td(gui.Label(_("Mute:  ")),
						colspan= 1, align=1);
		muteSwitch= gui.Switch(value=hacks['mute'], name='theater-switch-mute');
		muteSwitch.connect(gui.CLICK, self.muteSwitchState);
		theaterTable.td(muteSwitch, colspan= 2, align= -1);
		
		theaterDocument= gui.Document(width= geom['panel'].width,
									  height= geom['panel'].height,
									  align= 0);
		theaterDocument.add(theaterTable);
		self.add(theaterDocument, 0,10);
	
	def subtitleSwitchState(self):
		self.director.subtitler.on= not self.script.controls['theater-switch-subtitles'].value;
		hacks['subtitle']= self.director.subtitler.on
		changeSetting('Subtitle', self.director.subtitler.on)
	
	def muteSwitchState(self):
		hacks['mute']= not self.script.controls['theater-switch-mute'].value;
		changeSetting('Mute', hacks['mute'])
	
	#def changeBackdrop(self):
	#	back= self.script.controls['backdrop'].value;
	#	self.script.setBackdrop(backdrop.Backdrop(back));
	
class Tab(gui.Table):
	"""
	The tab holds five buttons that let you switch between panels.
	"""
	def __init__(self, script):
		gui.Table.__init__(self,
						   width= geom['tab'].width,
						   height= geom['tab'].height);
		
		self.script= script;
		
		panels= [FilePanel, BackdropPanel, ActorPanel, WritePanel, TheaterPanel];
		curPanel= 0;
		
		self.activePanel= panels[curPanel](self.script);
		self.activePanel.build();
		self.panelHolder= gui.Container(width= geom['panel'].width,
										height= geom['panel'].height);
		self.panelHolder.add(self.activePanel, 0, 0);
		
		self.tabGroup= gui.Group('tab-group-panels', panels[curPanel]);
		self.tabGroup.connect(gui.CHANGE, self.changePanel);
		
		buttonHeight= geom['tab'].height / len(panels) * 3 / 5;
		buttonWidth= geom['tab'].width * 3 / 5;
		self.panelLabels= {}
		for aPanel in panels:
			self.tr();
			panelLabel= gui.Label(aPanel.name,
								  name='tab-label-panels-'+aPanel.name);
			self.panelLabels[aPanel] = panelLabel
			aPanel.sourceTab= self
			panelTool= gui.Tool(self.tabGroup, panelLabel, aPanel, 
								width=buttonWidth,
								height=buttonHeight,
								name='tab-tool-panels-'+aPanel.name);
			self.td(panelTool, style={'padding': 10})

	def changePanel(self):
		self.activePanel.tearDown();
		self.activePanel.removeAll();
		self.panelHolder.remove(self.activePanel);
		self.activePanel= self.tabGroup.value(self.script);
		self.activePanel.sourceTab= self
		self.activePanel.build();
		self.panelHolder.add(self.activePanel, 0, 0);
		
	def reload(self):
		for aPanel, aPanelLabel in self.panelLabels.items():
			aPanelLabel.value = translate(aPanel.name)