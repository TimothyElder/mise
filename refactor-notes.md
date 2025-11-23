
2.	Extract a DocumentBrowserWidget that owns:
	•	back_button, file_list, upload_button
	•	populate_file_list, go_back, handle_upload_clicked, file context menu
3.	Extract a DocumentViewerWidget that owns:
	•	document_viewer
	•	display_file_content, open_text_context_menu, assign_code_to_selection, refresh_highlights
4.	Reduce ProjectWidget to:
	•	wiring the splitter
	•	constructing ProjectRepository, browser, viewer, code manager
	•	connecting signals between them
	•	closeEvent




	The architecture we are trying to do is to make PRojectWidget the controller so that everything traces through it and not between 

	•	Browser → emits documentActivated
	•	ProjectWidget → receives it, calls viewer.load_document
	•	Viewer → loads file + highlights
	•	CodeManager → when codes change, emits codes_updated, ProjectWidget already wired that to viewer.refresh_highlights

# Signals and Slots logic 

In Qt a primary functionality is the use of signals and slots to route events to triggers and the basic logic of these are that 

1. You declare a signal type as in:	`documentActivated = Signal(int, str)`, which says "There exists an event called documentActivated which carries two values: an int and a string." This is technically called an "event channel" and doesn't itself do anything at all.

2. Emit the signal upon the activation of some event/function as in: `self.documentActivated.emit(doc_id, path_str)` which says "Fire the event now; send these values over that channel."

3. A slot is just a normal Python function that has been connected to a signal. So this part is a little hard to parse but a function that is activated by a signal is blind to the signal and the slot as it is just a function, such as:

```py
def on_document_activated(self, doc_id, path_str):
    self.viewer.load_document(doc_id, Path(path_str))
```

As you can see there is no Qt syntax invoked in this function, and it is made a "slot" activated by the emission of a signal when it is connected to the signal/event channel by including: `browser.documentActivated.connect(self.on_document_activated)`

Some notes on Classes and functions:

- classes include type hints that are not enforced at run time and are declared in the init statement as:

	```py
	class MyClass:
    thing = "a variable in the class"
    
    def __init__(self, parameter1: int, parameter2: str):
	```
- functions can include returned type hints which is declared as:

	```py
	def is_pathname_valid(pathname: str) -> bool:
	```

this promises a boolean type object is returned from the function. 
