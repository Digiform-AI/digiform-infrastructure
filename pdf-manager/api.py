from flask import Flask, current_app, request
from digiFormClasses import Member, Organization, Server

class Api:

    app = Flask(__name__)
    server = Server() # Make new static test server

    myOrg = server.createOrg("ABC Construction")
    newForm = myOrg.generateNewForm("sample.pdf", "My Form", "01/01/01")

    myMember = Member("Test", "Member")
    myOrg.addMember(myMember)

    myOrg.sendFormRequest(newForm, myMember)
    myMember.selectForm(myOrg, 0) # Select this form for updates

    inspForm = myOrg.generateNewForm("inspection.pdf", "Inspection", "01/01/01")
    myOrg.sendFormRequest(inspForm, myMember)
    myMember.selectForm(myOrg, 1) # Select this form for updates


    # Member submits the form they are currently editing
    @app.route('/submitForm/', methods = ['GET','POST'])
    def submitCurrentForm():
        res = request.body
        for key in res.keys():
            value = res[key]["value"] # Dictionary of field name : field value, looking for key "value"
            Api.myMember.respondToField(int(key), value) # Respond to each field

        Api.myMember.submitFormResponse()
        return "Submitted "+Api.myMember.currentForm.name
    
    # Member saves current form
    @app.route('/saveForm/', methods = ['GET', 'POST'])
    def saveForm():
        res = request.body
        for key in res.keys():
            value = res[key]["value"] # Dictionary of field name : field value, looking for key "value"
            Api.myMember.respondToField(int(key), value) # Respond to each field

        # Same as above submit function but just stores and does not submit

    # This member updates a value for the active form
    # This is not used anymore because we instead want to just send all values at once
    @app.route('/updateField/<fieldIndex>/<newVal>/', methods = ['GET'])
    def updateField(fieldIndex, newVal):

        print(newVal)

        Api.myMember.respondToField(int(fieldIndex), newVal)
        return "Successfully set "+Api.myMember.currentForm.fields[int(fieldIndex)].name+" to "+newVal+"!"



    # This member will retrieve all its form requests
    @app.route('/getAllForms/', methods = ['GET'])
    def getAllForms():
        
        
        dict = {  }
        for form in Api.myMember.activeForms:

            dict.update( {form.formID: 
                          {"index": form.formID,
                           "complete": form.complete, 
                           "name": form.name, 
                           "due": form.due, 
                           "organizer": form.org.name}} )

        return dict
    
    # View this form that belongs to this member
    # Specific form details from id. This id is not index of activeForms. We must search active forms for this formID.
    @app.route('/getForm/<id>/', methods = ['GET'])
    def getForm(id):
        form = None
        for f in Api.myMember.activeForms:
            if f.formID == int(id):
                form = f
                break
        if form:
            # We found the form! TODO: Also return the path so it can be printed
            response = {"data": 
                        {"index": form.formID,
                         "complete": form.complete, 
                         "name": form.name, 
                         "due": form.due, 
                         "organizer": form.org.name}}

            # Now add the fields
            # NOTE: I included the height of the containing page for coordinate localization.
            fields = {}
            numPages = 0
            for field in form.fields:

                # Keep track of the total number of pages
                if field.pageIndex > numPages:
                    numPages += 1

                fields.update( 
                    { field.index: 
                     {"name": field.name, 
                      "index": field.index, 
                      "type": field.type,
                      "value": field.value,
                      "rect": field.rect,
                      "pageHeight": field.pageHeight,
                      "pageWidth": field.pageWidth,
                      "pageIndex": field.pageIndex,

                      "singleSelectionOnly": field.singleChoice,
                      "groupName": field.choiceGroup,
                      "choiceName": field.choiceValue,
                      } } )
            # # temporary for testing without api
            # checkbox = (abs(h/w) > 0.9 and abs(h/w) < 1.1)

            # # final code once hooked up to api

            # for field in fields:
            #     textFromCoordinates(field.rect[0], field.rect[1], field.rect[2], field.rect[3], field.pageHeight, field.type == "checkbox")
                
            response.update( {"fields": fields} )
            
            response.update( { 'pages': numPages + 1 } )
            return response
        else:
            return "404 Form not found!"
    
    
    def __init__(self):
        
        {
            #self.app.run(debug=True, port= 5000)
        }

Api()


