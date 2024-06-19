import xml.etree.ElementTree as ET
import zlib
import base64
import os

checkpoint_path = input("Please enter the path to the checkpoint XML file: ")
vbm_path = input("Please enter the path to the VBM file: ")
output_path = input("Please enter the path to save the new checkpoint file: ") 

def import_cloud_checkpoint_vbm(checkpoint_path, vbm_path, output_path):
    try:
        # Loading existing checkpoint to edit
        tree = ET.parse(checkpoint_path)
        root = tree.getroot()
        
        # Reading new Vbm and compressing it using zlib best compression [9]
        with open(vbm_path, "rb") as f:
            vbm_bytes = f.read()
        
        compressed_vbm = zlib.compress(vbm_bytes, level=zlib.Z_BEST_COMPRESSION)
        
        # Turning compressed data into a base64 string
        base64_compressed_vbm = base64.b64encode(compressed_vbm).decode('utf-8')
        
        # Check for the existence of the 'Vbm' element with 'InlineContent' attribute
        vbm_element = root.find('.//Vbm')
        if vbm_element is None or 'InlineContent' not in vbm_element.attrib:
            # Element or attribute not found, bail out with an error message
            print("Error: The XML file does not contain a 'Vbm' element with an 'InlineContent' attribute.")
            return
        
        # Replacing the Vbm inline content in existing checkpoint with newly generated one
        vbm_element.set('InlineContent', base64_compressed_vbm)
        
        # Saving new checkpoint as a separate file to output_path
        # Ensure the output_path includes a filename, not just a directory
        output_file_path = os.path.join(output_path, "modified_checkpoint.xml")
        tree.write(output_file_path)
        print(f"VBM imported successfully. New XML file saved to: {output_file_path}")
    
    except ET.ParseError:
        print("Error: The file provided is not a valid XML file.")
    except IOError as ex:
        print(f"Error: An IOError occurred: {ex}")
    except zlib.error as ex:
        print(f"Error: There was an issue compressing the data: {ex}")
    except Exception as ex:
        print(f"An unexpected error occurred: {ex}")

import_cloud_checkpoint_vbm(checkpoint_path, vbm_path, output_path)