import streamlit as st
import ifcopenshell
import ifcopenshell.util
from ifcopenshell.util.selector import Selector
import ifcopenshell.util.placement 
import ifcopenshell.api
import numpy as np
import tempfile
from vendor import ifcpatch
import os
import time

def move_to_origin(ifc_file, guid):
    part = ifc_file.by_guid(guid)
    old_matrix = ifcopenshell.util.placement.get_local_placement(part.ObjectPlacement)
    # st.write(old_matrix)
    new_matrix = np.eye(4)
    # st.write(new_matrix)
    ifcopenshell.api.run("geometry.edit_object_placement", ifc_file, product=part, matrix=new_matrix)

    # Save the modified IFC file to a temporary location and return the path
    # output_path = tempfile.mktemp(suffix=".ifc")
    # ifc_file.write(output_path)
    return ifc_file


st.title('BIMease: extract an IFC Element')

st.markdown("""Welcome to the BIMease Platform!

Ever wanted to quickly extract an object from a large BIM model for your own project? You're in the right place. Upload your BIM model, input the GUID, and voila—your object is yours, effortlessly.

Built on the robust framework of IfcOpenShell, the aim of BIMease is to simplify your BIM tasks. If you find BIMease useful, consider "buying me a coffee" to support the continued development of straightforward IFC tools. You can also support the innovative IfcOpenShell team by clicking here.

Jump in, and experience a streamlined BIM workflow like never before!

""")

uploaded_file = st.file_uploader("Choose an IFC file", type=['ifc'])
guid = st.text_input("Enter the GUID of the element to move:")


if uploaded_file and guid:
    with st.spinner("Your file is being extracted..."):
        time.sleep(2)
        tfile = tempfile.NamedTemporaryFile(delete=False) 
        tfile.write(uploaded_file.read())
        temp_path = tfile.name
        ifc = ifcopenshell.open(tfile.name)
        selector = Selector()

        # Collect all GUIDs in the model
        existing_guids = [elem.GlobalId for elem in ifc.by_type("IfcRoot")]

        # Check if the provided GUID exists
        if guid in existing_guids:
            st.write(f"The provided GUID {guid} has been found!")
            guid_exists = True
        else:
            st.write(f"The provided GUID {guid} does not exist in the model.")
            guid_exists = False


        if guid_exists == True:
            #Select IfcElement using by_guid
            element = ifc.by_guid(guid)
            # st.write("IFC entry for your selected element:")
            # st.write(element)

            #Select IfcElement using parser
            element_selector = selector.parse(ifc, f"#{guid}") # Equivalent to ifc.by_guid('2MLFd4X2f0jRq28Dvww1Vm')
            # st.write("IFC entry for your selected element obtained using Selector:")
            # st.write(element_selector)

            #Extract IfcElement using ifcpatch
            # extracted_ifc = ifcpatch.execute({"input": ifc, "file": ifc, "recipe": "ExtractElements", "arguments": ["2Iv7PUUCP1WPtBmz797eLa"]}) 
            extracted_ifc = ifcpatch.execute({"input": ifc, "file": ifc, "recipe": "ExtractElements", "arguments": [f"{guid}"]})  
            # st.write(extracted_ifc)
            
            extracted_ifc = move_to_origin(extracted_ifc, guid)

            temp_file_path = tempfile.mktemp(suffix='.ifc')
            extracted_ifc.write(temp_file_path)

            # Read the temporary file into a binary variable
            with open(temp_file_path, 'rb') as f:
                extracted_ifc_content = f.read()

            # Delete the temporary file
            os.remove(temp_file_path)

            # Create a download button for the extracted IFC file
            download_button = st.download_button(
                label="Download Extracted IFC File",
                data=extracted_ifc_content,
                file_name='BIMease.ifc',
                mime='application/octet-stream'
            )