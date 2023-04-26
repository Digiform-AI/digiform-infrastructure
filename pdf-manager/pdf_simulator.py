from pypdf import PdfReader, PdfWriter
from pdfStructure import pdfForm, pdfElement, Consts
from pypdf.generic import NameObject,TextStringObject
from pypdf.constants import *
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate
from reportlab.lib.utils import ImageReader
import os, io, csv

import xlsxwriter


import shutil


# This is the first point of contact with the pdf from the Organization side once they upload
# We first must gather a list of all field names, their type, and location
# From there, we can send the data of the field names and type to the user side for the "Electronic Entry" mode.
   
    # Lifecycle of user electronically submitting pdf :
    # 1) Parse the BLANK pdf to gather a list of field names, and types (text or checkbox)
    # 2) Send this data to mobile users when we submit the form and display as a list where user can set values.
    # 3) When user submits responses electronically back to server, we interpret and WRITE responses to a duplicate of BLANK pdf


class PdfGenerator():

    # Create a pdf from desktop site. Given fields with name, type, default value.
    def createPdf(fields, title, due, org):
        path = title+".pdf"
        spacing = 50


        c = canvas.Canvas(path)
        c.setFont("Courier", 20)
        c.drawCentredString(300, 800, title)

        c.setFont("Courier", 14)
        form = c.acroForm

        # We need to find how far to the right to place all fields, based on the longest title.
        max = 0
        for field in fields:
            name = None
            if field.type == Consts.mcDisplay:
                name = field.choiceValue
            else:
                name = field.name
            if len(name) > max:
                max = len(name)
        # We know the longest string is max. Make x
        x = max * 11
  


        ht = 700
        visitedGroups = []
        for field in fields[:]:

            # Start a new page and reset ht if we are near the bottom
            if (ht <= 10): # less than 10px at bottom then start new page
                c.showPage()
                ht = 800 # reset our position to top of page
                c.setFont("Courier", 14)
            
            if field.type == Consts.mcDisplay:
                # Check if group has been visited yet. If not, add title
                if field.choiceGroup not in visitedGroups:
                    visitedGroups.append(field.choiceGroup)
                    c.drawString(x, ht, field.choiceGroup)
                    ht -= spacing
                else:
                    # Bring choices close together
                    ht+= (spacing/2)
                
                c.drawString(10, ht+5, field.choiceValue+": ")

                # Name of field used to be field.choiceValue, this is bad it should be field.name to maintain Group:Choice form!
                # This display string, above, should stay as field.choiceValue.
                form.checkbox(name=field.name, tooltip='Multiple Choice',
                x= x, y= ht, buttonStyle='cross')

            elif field.type == Consts.checkBoxDisplay:
                c.drawString(10, ht+5, field.name+": ")

                form.checkbox(name=field.name, tooltip='Checkbox',
                x= x, y= ht, buttonStyle='cross')

            elif field.type == Consts.textFieldDisplay:
                c.drawString(10, ht+15, field.name+": ")

                form.textfield(name=field.name, tooltip='Text',
                x = x, y= ht, width= (620 - 2*x))

            ht -= spacing # Decrease height regardless
        c.save()


        # All fields created, return path to org so they can generate form
        return PdfGenerator.generateForm(path, title, len(org.forms), due, org)
        # Handles populating rect and page height properties mostly


    def generate_csv(form):

        with open(form.name+'.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            
            visitedGroups = [] # Used to keep track of radio groups so we only display once
            fieldNames = [] # the list of names which we will display as the first row
            
            # Add the names of the fields to the top row as a header
            for field in form.fields:
                if (field.type == Consts.mcDisplay):
                    group = field.choiceGroup

                    if group not in visitedGroups:
                        # Add this group field 
                        fieldNames.append(group)
                        visitedGroups.append(group)

                else: # Not a multiple choice so just display its name
                    fieldNames.append(field.name)
        
            # Write the names as a row
            writer.writerow(fieldNames)

            # Next add the data values for each response, first we include a space
            writer.writerow([""])
            
            
            for response in form.responses:
                
                # Each person gets their own row, an array of responses
                answers = []
                visitedGroups = []
                
                for field in response.fields:
                    if (field.type == Consts.checkBoxDisplay):

                        if (field.value in Consts.checkBoxYesState):
                            value = Consts.checkBoxDisplayYes
                        else:
                            value = Consts.checkBoxDisplayNo


                        answers.append(value) # Write the checkbox response in a readible fashion (yes/no)

                    # MANAGE DISPLAY OF MULTIPLE CHOICE
                    elif (field.type == Consts.mcDisplay):
        
                        group = field.choiceGroup

                        if group not in visitedGroups:
                            visitedGroups.append(group) # Avoid doing this group twice
                            values = []
                            for f in response.fields:
                                # Iterate again over all fields to find all responses of this group
                                if (f.type == Consts.mcDisplay):
                                    
                                    g = f.choiceGroup
                                    v = f.choiceValue

                                    # This is in our current target group
                                    if (group == g):
                                        # We responded yes to this field for this group
                                        if (f.value in Consts.checkBoxYesState):
                                            
                                            values.append(v)
                            # We have aquired all the response values for this option in values[].
                            results = ""
                            last_i = len(values) - 1
                            if not values:
                                results = "None"
                            else:
                                for i in range(len(values)):
                                    if i == last_i:
                                        results += values[i]
                                    else:
                                        # We dont use , here because that would denote a new cell
                                        results += (values[i] + " & ")
                            answers.append(results) # store our multiple choice selections as a cell for this column
                            

                        else: # Already did this group!
                            continue


                    # All other types just write its value! (text)
                    # If its nothing, we denote NO RESPONSE?
                    else:
                        answers.append(field.value)
                        
                        # Note if no response it will append nothing and show as ,,,

                # Done with this person, add a row of their answers
                writer.writerow(answers)
            file.close()


    # Generate excel from response
    def generateExcel(form):
        workbook = xlsxwriter.Workbook(form.name+".xlsx")
        worksheet = workbook.add_worksheet(form.name)
        visitedGroups = [] # Used to keep track of radio groups so we only display once

        # First add the column headers
        col = 0
        
        for field in form.fields:
            if (field.type == Consts.mcDisplay):
               
                
                group = field.choiceGroup

                if group not in visitedGroups:
                    # Add this group field 
                    worksheet.write(0, col, group)
                    visitedGroups.append(group)
                    col += 1
            else: # Not a multiple choice so display its name
                worksheet.write(0, col, field.name)
                col+=1
       
        # Next add the data values for each response
        row = 1
        
        for response in form.responses:
            
            # Each response has it's own row.
            row += 1
            col = 0
            visitedGroups = []
            
            for field in response.fields:
                if (field.type == Consts.checkBoxDisplay):

                    if (field.value in Consts.checkBoxYesState):
                        value = Consts.checkBoxDisplayYes
                    else:
                        value = Consts.checkBoxDisplayNo

                    worksheet.write(row, col, value) # Write the checkbox response in a readible fashion (yes/no)

                # MANAGE DISPLAY OF MULTIPLE CHOICE
                elif (field.type == Consts.mcDisplay):
       
                    group = field.choiceGroup

                    if group not in visitedGroups:
                        visitedGroups.append(group) # Avoid doing this group twice
                        values = []
                        for f in response.fields:
                            # Iterate again over all fields to find all responses of this group
                            if (f.type == Consts.mcDisplay):
                                
                                g = f.choiceGroup
                                v = f.choiceValue

                                # This is in our current target group
                                if (group == g):
                                    # We responded yes to this field for this group
                                    if (f.value in Consts.checkBoxYesState):
                                        
                                        values.append(v)
                        # We have aquired all the response values for this option in values[].
                        results = ""
                        last_i = len(values) - 1
                        if not values:
                            results = "None"
                        else:
                            for i in range(len(values)):
                                if i == last_i:
                                    results += values[i]
                                else:
                                    results += (values[i] + ", ")
                        worksheet.write(row, col, results)
                        

                    else: # Already did this group!
                        continue


                # All other types just write its value! (text)
                else:
                    worksheet.write(row, col, field.value)

                col += 1
        worksheet.autofit()
        workbook.close()

        
    # This function will take an existing form response object
    # that has been return with it's responses by a client and create a new blank forum, then fill it in.
    # NOTE: This means we must store 'blank' copy as an attribute in the form object, which will server 3 purposes
        # 1) If we implement client endpoint on the web server, they can view the blank copy there and fill it on a PC
        # 2) We can display a visual of the pdf to users on the app
        # 3) When the server recieves a response in object form, it can use the 'blank' to make the duplicate and fill in

    # Should take a form RESPONSE
    def generatePdf(response, formFolder): #formFolder passed as 'path'
        # Get the form that this response associates to
        # org = Server.getOrgByID(response.orgID)
        org = response.org
        sourceForm = org.getFormByID(response.formID)

        # Used to grab by ID: org.members[response.responderID]
        newFile = formFolder + response.responder.firstName+" "+response.responder.lastName +".pdf" # Name it responder.pdf
        # shutil.copy(sourceForm.path, newFile)

        reader = PdfReader(sourceForm.path)

        writer = PdfWriter()
        writer.append_pages_from_reader(reader)
        writer.set_need_appearances_writer()
        responses = response.fields
        values = []

        # For each response
        for r in responses[:]:


            # If this is a checkbox or radio button, we must convert the "No" to "/Off", etc so pdf can understand.
            if (r.type == Consts.checkBoxDisplay or r.type == Consts.mcDisplay):

                if (r.type == Consts.mcDisplay):
                    pass

                if (r.value == Consts.checkBoxDisplayYes):
                        if r.generated:
                            r.value = Consts.checkBoxYesState[1]
                        else: # use /0
                            r.value = Consts.checkBoxYesState[0]
                else:
                        r.value = Consts.checkBoxNoState
            # Add to our field dict for fields to be updates

            values.append(r.value)


        """(re purposed update_page_form_field_values)"""
        k = 0
        # On each page 
        for page in writer.pages:
            
            # For each annotation (j is index of annot) on this page
            for j in range(len( page[PageAttributes.ANNOTS] )):

                writer_annot = page[PageAttributes.ANNOTS][j].get_object()  # type: ignore
                # print(j, k)
                
                # Check if we should ignore this annotation, i.e. if its name is not one of our responses
                skip = True
                for r in responses:
                    if (r.name == writer_annot.get(FieldDictionaryAttributes.T)):
                        skip = False # Don't skip this one

                if skip: # Skip this!
                    continue #without incrimenting k

               
                # Update the value. Buttons get an extra value tag
                if writer_annot.get(FieldDictionaryAttributes.FT) == "/Btn":
                    writer_annot.update(
                        {
                            NameObject(
                                AnnotationDictionaryAttributes.AS
                            ): NameObject(values[k])
                        }
                    )
                 
                
                writer_annot.update(
                {
                    NameObject(FieldDictionaryAttributes.V): 
                    TextStringObject( values[k] )
                }
                )
                # NOTE: Make read only did not fix invisible text issue!
                # writer_annot.update({NameObject("/Ff"): NumberObject(1)})

                k += 1 # Update total respect field index (index holds across pages)
        


        # write "output" to pypdf-output.pdf
        with open(newFile, "wb") as output_stream:
            writer.write(output_stream)
        output_stream.close()

        #fillpdfs.flatten_pdf(newFile, 'flat.pdf', True)

        # now overlay signatures ontop of it
        signed_pdf = PdfGenerator.addSignatures(newFile, responses)

        return signed_pdf # return path to upload to s3

        #NOTE: Attempt to flatten did not fix invisible text. Try converting to image perhaps
        




    # given fields, return member name
    # NOTE this gets called after extract, and before saving response.
    def getNameByFields(fields):
        for field in fields:
            # Field says firstname, so store the first name
            if field.name in Consts.firstNameFields:
                firstName = field.value.capitalize()

            # Field says name so its probably first and last
            if field.name in Consts.nameFields:
                splitName = field.value.split(" ")
                
                # Store first and maybe last name
                firstName = splitName[0].capitalize()
                if len(splitName) == 2:
                    lastName = splitName[1].capitalize()

            # We are given last name so store last name
            if field.name in Consts.lastNameFields:
                lastName = field.value.capitalize()
        
        return [firstName, lastName]
    
    # This function will generate a new form object. It can be thought of as "Starting an Event", and members of the organization
    # are per say "Invited to the event". In this case, that means being sent a "pdfRequest" object - a request to fill in
    # the fields. This form object will be referenced in the code for Organization, when sendRequest(form, client) is called.




    
    # We also create a directory where input files are uploaded to and stored
    def generateForm(path, title, formID, due, org):

        if not os.path.isdir("input/"+title):
            os.mkdir("input/"+title)

        reader = PdfReader(path)
        
    
        myFields = []
        fieldIndex = 0
        curFieldPage = 0


        for page in reader.pages:
            
            if "/Annots" in page:
                # Store the heights so we can flip the orientation on Textract coordinate mapping (to top-to-bottom)
                

                for annot in page["/Annots"]:
      
                    fieldData = annot.get_object()
                    
                    
                    try:
                            curFieldName = fieldData["/T"]
                    except: # Key error /T - watermark?
                        pass#print(fieldData)
                    


                    if (fieldData["/Subtype"] == "/Widget"):
                        
                        
                        curFieldType = ""
                        curFieldValue = ""
                        curFieldIndex = fieldIndex
                        curFieldRect = fieldData["/Rect"]
                        curFieldGenerated = True
                        curFieldPageHeight = page.mediabox.height
                        curFieldPageWidth = page.mediabox.width
                        try:
                            curFieldName = fieldData["/T"]
                        except: # Key error /T
                            continue # Skip this bad data type
                            #curFieldName = "Unsupported_"+str(fieldIndex)

                        try:
                            fieldTypeID = fieldData["/FT"]
                        except: # Unsupported field type (MC?)
                            # fieldTypeID = "UnsupportedType"
                            continue # Skip this bad data type

                        # Get whether the field came from a generated form by looking for '/TU'
                        try:
                            fieldData["/TU"]
                        except:
                            # If this fails it was not generated
                            curFieldGenerated = False

                        #print(curFieldName)

                        # Handle check box metadata
                        # Is it a check box or radio button
                        if (fieldTypeID == Consts.checkTypeID):
                            
                            if (curFieldName.find(":") != -1):
                                curFieldType = Consts.mcDisplay
                            else: 
                                 # Checkbox only code
                                 curFieldType = Consts.checkBoxDisplay
                            try:
                                curFieldValue = fieldData["/V"]
                            except:
                                # Field is empty!
                                curFieldValue = ""
                            


                            # Readable values to machine values
                            # System created form has /V for yes to be /Yes, no to be /Off.
                            # Adobe forms has yes to be /0, and no to be /On. So we fix this by making an array of Consts
                            if (curFieldValue in Consts.checkBoxYesState):
                                curFieldValue = Consts.checkBoxDisplayYes
                            else:
                                curFieldValue = Consts.checkBoxDisplayNo

                        # Handle text box
                        elif (fieldTypeID == Consts.textTypeID):
                            curFieldType = Consts.textFieldDisplay
                            try:
                                curFieldValue = fieldData["/V"]
                            except:
                                # Field is empty!
                                curFieldValue = ""

                        # Append this field to our list
                        curField = pdfElement(curFieldName, curFieldType, curFieldValue, curFieldIndex, curFieldRect, curFieldGenerated, curFieldPageHeight, curFieldPageWidth, curFieldPage)
                        myFields.append(curField)
                        fieldIndex = fieldIndex + 1
            curFieldPage+=1

            

        return pdfForm(title, formID, due, org, myFields, path)

    # Creates borders around the text to tell user where to write responses
    # Also creates a border on the outside of the document so we know where to crop after the scan
    # Must be called from the print button to print this form (path returned)
    def printForm(form):
        newPath = form.path.replace(".pdf", "-print.pdf")
        shutil.copy(form.path, newPath) # Create a copy to put the boxes onto

        existing_pdf = PdfReader(open(newPath, "rb")) # Store the existing pdf, the copy which we will overlay the boxes to
        output = PdfWriter() # designate a file for the final output

        stage_path = 'rectangles'

        # make sure the staging directory exists
        if not os.path.exists(stage_path):
            os.mkdir(stage_path)
        

        # For each page, generate a page on a new buffer of just boxes. Later, we overlay the two.
        for i in range(len(existing_pdf.pages)):
            w, h = 0, 0

            # to gather the page size
            for field in form.fields:
                if field.pageIndex == i: # Make sure this field is on this page!
                    w, h = field.pageWidth, field.pageHeight # Save this page's width and height to draw a surround box
                    break

            # we can now make the canvas for this page because we know the size
            # if we get an error there may be no fields on the page. Detect that above and set pagesize to letter if so
            cur_page = "page"+str(i + 1)+".pdf"
            can = canvas.Canvas(os.path.join(stage_path, cur_page), pagesize=(w,h))

            
            # Make each border for a field on this page, only
            for field in form.fields:
                if field.pageIndex == i: # Make sure this field is on this page!
                    can.rect(field.rect[0], field.rect[1], field.rect[2] - field.rect[0], field.rect[3] - field.rect[1])

            # Make border around entire page (for cropping), independent of print margin settings
            can.setLineWidth(2)
            can.rect(0,0,w,h)

            can.save() # page is done

            
        
        # Merge all pages together
        for i in range(len(existing_pdf.pages)):
            
            new_page_pdf = PdfReader( open(os.path.join(stage_path, "page"+str(i + 1)+".pdf"), "rb"))
            page = existing_pdf.pages[i]
            page.merge_page(new_page_pdf.pages[0])
            output.add_page(page)
            

        outputStream = open(newPath, "wb")
        output.write(outputStream)
        outputStream.close()

        # clear the staging directory as we have used the new pages of rectangles
        files = os.listdir(stage_path)

        for file in files:
            path = os.path.join(stage_path, file)
            if os.path.isfile(path):
                os.unlink(path)

        return newPath
    
    # draw signatures ontop of the pdf at the correct location
    def addSignatures(path, fields):

        existing_pdf = PdfReader(open(path, "rb")) # Store the existing pdf, the copy which we will overlay the boxes to
        output = PdfWriter() # designate a file for the final output

        stage_path = 'signature_stage'

        # make sure the staging directory exists
        if not os.path.exists(stage_path):
            os.mkdir(stage_path)
        

        # For each page, generate a page on a new buffer of just boxes. Later, we overlay the two.
        for i in range(len(existing_pdf.pages)):
            w, h = 0, 0

            # to gather the page size
            for field in fields:
                if field.pageIndex == i: # Make sure this field is on this page!
                    w, h = field.pageWidth, field.pageHeight # Save this page's width and height to draw a surround box
                    break

            # we can now make the canvas for this page because we know the size
            # if we get an error there may be no fields on the page. Detect that above and set pagesize to letter if so
            cur_page = "page"+str(i + 1)+".pdf"
            can = canvas.Canvas(os.path.join(stage_path, cur_page), pagesize=(w,h))

            
            # For each signature field on this page find the image and add it
            for field in fields:
              
                if field.name.lower().find('signature') != -1:
                    if field.pageIndex == i: # Make sure this field is on this page!
                        img = 'documents/signatures/' + field.name + '.png'
                        can.drawImage(img, field.rect[0], field.rect[1], field.rect[2] - field.rect[0], field.rect[3] - field.rect[1])

            can.save() # page is done

            
        
        # Merge all pages together
        for i in range(len(existing_pdf.pages)):
            
            new_page_pdf = PdfReader( open(os.path.join(stage_path, "page"+str(i + 1)+".pdf"), "rb"))
            page = existing_pdf.pages[i]
            page.merge_page(new_page_pdf.pages[0])
            output.add_page(page)
            

        outputStream = open(path, "wb")
        output.write(outputStream)
        outputStream.close()

        # clear the staging directory as we have used the new pages of images
        files = os.listdir(stage_path)

        for file in files:
            path = os.path.join(stage_path, file)
            if os.path.isfile(path):
                os.unlink(path)

        return path
    
    # decrypt the given pdf and return the path to the new doc
    def decrypt_pdf(path):
        pdf_writer = PdfWriter()
        pdf_reader = PdfReader(path)

        # add each page from the original PDF to the new PDF writer
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            pdf_writer.add_page(page)

        # remove the encryption from the new PDF
        pdf_writer.encrypt("", "")

        file_name, file_extension = os.path.splitext(path)

        # create a new file path for the decrypted PDF
        new_file_path = file_name + "-decrypted" + file_extension

        # write the new PDF to disk
        with open(new_file_path, "wb") as output_file:
            pdf_writer.write(output_file)

        return new_file_path