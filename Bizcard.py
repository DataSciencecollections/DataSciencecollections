
#=========================================================== /    /   Dash Board   /   / =========================================================#

#[Dashboard Library]

import streamlit as st

#[DataFrame Libraries]

import pandas as pd

#[Bizcard Scanning libraries]

import numpy as np
from streamlit_option_menu import option_menu
import io
from PIL import Image
import easyocr
import re
import io
import sqlite3

#to find image
def text_image(path):

  image=Image.open(path)

  #convert image into array

  image_array=np.array(image)
  reader= easyocr.Reader(['en'])
  text=reader.readtext(image_array,detail=0)

  return text, image

#function define

def extract_text(texts):
  data = {"Cardholder_name":[],
          "Comapany_name":[],
          "Designation":[],
          "Email":[],
          "Contacts":[],
          "Website_address":[],
          "Pincode":[],
          "Area":[]
          }

  #to get cardholder name

  data["Cardholder_name"].append(texts[0])

  #to get designation

  data["Designation"].append(texts[1])

  for i in range(2,len(texts)):

# to get contacts
    if texts[i].startswith("+") or (texts[i].replace("-","").isdigit() and "-" in texts[i]):
      data["Contacts"].append(texts[i])

#to get Email
    elif "@" in texts[i] in texts[i]:
      data["Email"].append(texts[i])

#to get Website

    elif "www" in texts[i] or "www." in texts[i] or "Www" in texts[i] or "WWW" in texts[i] or "wwW" in text[i]:
      data["Website_address"].append(texts[i])

 # To get PINCODE
    elif "TamilNadu" in texts[i] or "Tamil Nadu" in texts[i] or len(texts[i]) >= 6 and texts[i].isdigit():
        data["Pincode"].append(texts[i])

#to get company name

    elif re.match(r'^[A-Za-z]', texts[i]):
      data["Comapany_name"].append(texts[i])

# To get area

    elif re.findall("^[0-9].+, [a-zA-Z]+", texts[i]):
        data["Area"].append(texts[i].split(",")[0])
    elif re.findall("[0-9] [a-zA-Z]+", texts[i]):
        data["Area"].append(texts[i])

#handle NA values

  for key,value in data.items():
    if len(value)>0:
      con=" ".join(value)
      data[key]=[con]

    else:
      value = "NA"
      data[key]= [value]

  return(data)


#======================================================================//configuring streamlit//=========================================================================#

st.set_page_config(layout='wide')

#Title

st.title(':red[BIZCARDX DATA EXTRACTION WITH OCR]')

#option menu

with st.sidebar:
  select=option_menu("Main Menu",["HOME"])

  if select == "HOME":
    st.title(':blue[BIZCARDX DATA EXTRACTION WITH OCR]')
    st.write("*****BizcardX is likely a service or tool designed for extracting data from business cards using Optical Character Recognition (OCR) technology. Here's a breakdown of how such a system typically works:*****")
    st.write("*****Scanning the Business Card*****")
    st.write("*****Image Pre-processing*****")
    st.write("*****OCR Analysis*****")
    st.write("*****Text Extraction*****")
    st.write("*****Data Structuring*****")
    st.write("*****Output*****")
#TABS

tab1, tab2,tab3 = st.tabs(["DATA EXTRACTION","DATA MODIFICATION","DELETE"])

#===================================================================//extaction//======================================================================================#

with tab1:
  st.subheader(':blue[Data Extraction]')

  image= st.file_uploader("Upload the Business Care", type=["jpg", "jpeg", "png"])

  if image is not None:
    st.image(image, width=400)

    text,image=text_image(image)

    text_dic=extract_text(text)

    if text_image:
      st.success("Extracted Successfully")

      df=pd.DataFrame(text_dic)

 #=========================================================================//converting image into bytes//================================================================#

    Image_bytes=io.BytesIO()
    image.save(Image_bytes, format='png')

    img_data=Image_bytes.getvalue()

    #to create Dictionary

    image_to_bytes={"Image":[img_data]}

    df1= pd.DataFrame(image_to_bytes)

    #dataframe conversion

    Dataframe= pd.concat([df, df1], axis= 1)

    st.dataframe(Dataframe)


  #================================================================================//to create database//===============================================================#

    button1=st.button("save")

    if button1:
      mydb = sqlite3.connect("bizcard.db")
      cursor= mydb.cursor()

      #to create database
      create_table= """CREATE TABLE IF NOT EXISTS BizcardX (cardholder_name varchar(255),
                                                            company_name varchar(255),
                                                            designation varchar(255),
                                                            email varchar(150),
                                                            contacts varchr(255),
                                                            website_address text,
                                                            pincode varchar(150),
                                                            area varchar(255),
                                                            image text)"""

      cursor.execute(create_table)
      mydb.commit()                                               

#=======================================================================//insert datas into table//==================================================================#

      inser_query= """INSERT INTO BizcardX (cardholder_name,
                                            company_name,
                                            designation,
                                            email,
                                            contacts,
                                            website_address,
                                            pincode,
                                            area,
                                            image)
                                            
                                            values(?,?,?,?,?,?,?,?,?)"""

      value= Dataframe.values.tolist()[0]    #we have to select index
      cursor.execute(inser_query,value)
      mydb.commit()

      st.success("successfully saved")

#to create a preview button
    
  pattern= st.radio("select", ["None", "preview"])

  if pattern=="None":
    st.write("")

  if pattern=="preview":
    mydb = sqlite3.connect("bizcard.db")
    cursor= mydb.cursor()

    

    select_query="select * from BizcardX"

    cursor.execute(select_query)
    show_table=cursor.fetchall()
    mydb.commit()
    table_df= pd.DataFrame(show_table, columns=("Cardholder_name",
                                                "Comapany_name",
                                                "Designation",
                                                "Email",
                                                "Contacts",
                                                "Website_address",
                                                "Pincode",
                                                "Area",
                                                "Image"))
    st.dataframe(table_df)
#=========================================================== //  mofifying data // ====================================================================#
    with tab2:
        mydb = sqlite3.connect("bizcard.db")
        cursor= mydb.cursor()

        

        select_query="select * from BizcardX"

        cursor.execute(select_query)
        show_table=cursor.fetchall()
        mydb.commit()
        table_df= pd.DataFrame(show_table, columns=("Cardholder_name",
                                                    "Comapany_name",
                                                    "Designation",
                                                    "Email",
                                                    "Contacts",
                                                    "Website_address",
                                                    "Pincode",
                                                    "Area",
                                                    "Image"))
        
        col1,col2= st.columns(2)
        with col1:

          Name= st.selectbox("Select Name",table_df["Cardholder_name"])

        df2=table_df[table_df["Cardholder_name"]==Name]
        

        df3= df2.copy()
        

        col1,col2=st.columns(2)

        with col1:
          
          modified_name=st.text_input("NAME",df2["Cardholder_name"].unique()[0])
          mod_comp_name=st.text_input("comapanyname",df2["Comapany_name"].unique()[0]) 
          mod_designation=st.text_input("designation",df2["Designation"].unique()[0]) 
          mod_email=st.text_input("email",df2["Email"].unique()[0])
          mod_contact=st.text_input("contact",df2["Contacts"].unique()[0])

          df3["Cardholder_name"] = modified_name
          df3["Comapany_name"] = mod_comp_name
          df3["Designation"] = mod_designation
          df3["Email"] = mod_email
          df3["Contacts"] = mod_contact
        with col2:
          mod_website=st.text_input("website",df2["Website_address"].unique()[0])
          mod_pincode=st.text_input("pincode",df2["Pincode"].unique()[0])
          mod_area=st.text_input("area",df2["Area"].unique()[0])
          mod_image=st.text_input("image",df2["Image"].unique()[0])

          df3["Website_address"] = mod_website
          df3["Pincode"] = mod_pincode
          df3["Area"] = mod_area
          df3["Image"] = mod_image

        st.dataframe(df3)

        col1,col2= st.columns(2)

        with col1:
          button1=st.button("Modify")

        if button1:
          mydb = sqlite3.connect("bizcard.db")
          cursor= mydb.cursor()

          cursor.execute(f"DELETE FROM BizcardX WHERE Cardholder_name ='{Name}'")
          mydb.commit()

          inser_query= """INSERT INTO BizcardX (cardholder_name,
                                          company_name,
                                          designation,
                                          email,
                                          contacts,
                                          website_address,
                                          pincode,
                                          area,
                                          image)
                                          
                                          values(?,?,?,?,?,?,?,?,?)"""

          value= df3.values.tolist()[0]    #we have to select index
          cursor.execute(inser_query,value)
          mydb.commit()

          st.success("successfully modified")

#================================================================//delete zone//=============================================================================#
with tab3:

  mydb = sqlite3.connect("bizcard.db")
  cursor= mydb.cursor()


  col1,col2= st.columns(2)

  with col1:
    select_query="SELECT Cardholder_name FROM BizcardX"    #to delete unwanted data through name

    cursor.execute(select_query)
    show_table=cursor.fetchall()
    mydb.commit()

#to delete particular name with particular designation bcos same name have diff designation

    names=[]

    for i in show_table:
      names.append(i[0])


    select_name= st.selectbox("Select the Cardholder_name", names)

  with col2:
    select_query=f"SELECT Designation from BizcardX WHERE Cardholder_name= '{select_name}'"     #to delete unwanted data through designation

    cursor.execute(select_query)
    show_table=cursor.fetchall()
    mydb.commit()

    designation=[]

    for j in show_table:
      designation.append(j[0])
   

      select_designation= st.selectbox("Select the Designation", designation)

  if select_name and select_designation:
    col1,col2,col3= st.columns(3)

    with col1:

      st.write(f"Selected Name : {select_name}") 
      st.write("") 
      st.write("") 
      st.write("") 
      st.write(f"Selected Designation : {select_designation}")

    with col2:
      st.write("") 
      st.write("") 
      st.write("") 
      st.write("")

      Delete= st.button("DELETE", use_container_width= True)

      if Delete:

        cursor.execute(f"DELETE FROM BizcardX WHERE Cardholder_name = '{select_name}' AND Designation = '{select_designation}'")
        mydb.commit()

        st.warning("Deleted")






    



      







        

 





  










