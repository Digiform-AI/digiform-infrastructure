from digiFormClasses import Organization, Server, Member
from pdfStructure import pdfElement, Consts
from pdfManager import PdfGenerator
from api import Api

# Sample Driver code 
server = Server()

myOrg = server.createOrg("ABC Construction")
Bob = Member("Bob", "Smith")
Joe = Member("Joe", "Shmo")
Luna = Member("Luna", "Bird")

myOrg.addMember(Bob)
myOrg.addMember(Joe)
myOrg.addMember(Luna)

# Org creates the form
newForm = myOrg.generateNewForm("sample.pdf", "My Form", "01/01/01")

# Demonstrate creation of pdf document through frontend
fields = []
fields.append(pdfElement("First Name", Consts.textFieldDisplay, "", 0, None, True, None))
fields.append(pdfElement("Last Name", Consts.textFieldDisplay, "", 1, None, True, None))
fields.append(pdfElement("Address", Consts.textFieldDisplay, "", 2, None, True, None))
fields.append(pdfElement("$Gender:Male", Consts.mcDisplay, "", 3, None, True, None))
fields.append(pdfElement("$Gender:Female", Consts.mcDisplay, "", 4, None, True, None))
fields.append(pdfElement("Likes Dogs", Consts.checkBoxDisplay, "", 5, None, True, None))
webForm = myOrg.createPdfFromDesktop(fields, "Devin's Form", "02 / 30 / 23")

PdfGenerator.printForm(newForm)
PdfGenerator.printForm(webForm)


# Org sends the form to all members, Bob Recieves it (Bob)
myOrg.sendFormRequest(newForm, myOrg.members)

# Member clicks on the form our org just created.
# In practice, this will be set when a form is clicked in UI
# This object then will be used to display and prompt member to fill in the fields

Bob.selectForm(myOrg, 0)
Joe.selectForm(myOrg, 0)

#newForm.display() 

Bob.respondToField(0, "Bob Smith")
Joe.respondToField(0, "Joe Shmo")

Joe.respondToField(1, Consts.checkBoxDisplayYes)

Bob.respondToField(2, "Math")
Joe.respondToField(2, "Science")

Bob.respondToField(3, "Summer")
Joe.respondToField(3, "Fall")

# Demonstrate gender, a single response field being updated
Bob.respondToField(6, Consts.checkBoxDisplayYes)
Bob.respondToField(7, Consts.checkBoxDisplayYes)
Joe.respondToField(5, Consts.checkBoxDisplayYes)

# Bob likes cats
Bob.respondToField(4, Consts.checkBoxDisplayYes)

# Demonstrate symptoms, a multi response field being updated
Bob.respondToField(8, Consts.checkBoxDisplayYes)
Bob.respondToField(10, Consts.checkBoxDisplayYes)
Joe.respondToField(9, Consts.checkBoxDisplayYes)
Joe.respondToField(11, Consts.checkBoxDisplayYes)


#Submit the currently active form from the earlier selectForm call
# NOTE: This will occur from frontend when user presses submit button.
# Action: when server recieves it will download the document and store it in the correct directory.
Bob.submitFormResponse() 
Joe.submitFormResponse() 

# Demonstrate adding existing responses from organization submission
myOrg.addExisitngResponses()

# Generate excel 
PdfGenerator.generateExcel(newForm)
PdfGenerator.generateExcel(webForm)

#TODO: 
# Fix weird text being hidden
# CSV export option
# Make sure it works w professor's form
# Remove member functions
# Update member functions
# Fix the name function


# NOTE: Checkboxes are correctly ticked in input/MyForm, they just aren't in responses/MyForm, so it has to be a matter of semantics with /0
