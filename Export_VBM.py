import xml.etree.ElementTree as ET
import base64
import zlib
import os

def export_cloud_checkpoint_vbm():
    # Prompt the user for the XML checkpoint file path
    checkpoint_path = input("Please enter the path to the checkpoint XML file: ")
    
    # Print the given input path for debugging
    print(f"Checkpoint XML file path provided: {checkpoint_path}")
    
    # Determine the output file path by appending '_output.vbm' to the base name
    base_name = os.path.splitext(checkpoint_path)[0]
    vbm_path = f"{base_name}_output.vbm"
    
    # Print the determined output path for debugging
    print(f"Output VBM file path determined: {vbm_path}")
    
    try:
        # Read and parse the XML file
        tree = ET.parse(checkpoint_path)
        root = tree.getroot()

        # Check for the existence of the 'Vbm' element with 'InlineContent' attribute
        vbm_element = root.find('.//Vbm')
        if vbm_element is None or 'InlineContent' not in vbm_element.attrib:
            # Element or attribute not found, bail out with an error message
            print("Error: The XML file does not contain a 'Vbm' element with an 'InlineContent' attribute.")
            return

        # Extract the Base64-encoded text
        vbm_data_base64 = vbm_element.get('InlineContent')

        # Decode the Base64 data into bytes
        vbm_compressed_data = base64.b64decode(vbm_data_base64)

        # Decompress the data, assuming it includes a zlib header
        vbm_decompressed_data = zlib.decompress(vbm_compressed_data)

        # Write the decompressed data to the output file
        with open(vbm_path, 'wb') as vbm_file:
            vbm_file.write(vbm_decompressed_data)

        # Print a success message
        print(f"Export completed. Decompressed VBM file saved to: {vbm_path}")
    
    except ET.ParseError:
        print("Error: The file provided is not a valid XML file.")
    except base64.binascii.Error as ex:
        print(f"Error: There was an issue decoding the Base64 data: {ex}")
    except zlib.error as ex:
        print(f"Error: There was an issue decompressing the data: {ex}")
    except Exception as ex:
        print(f"An unexpected error occurred: {ex}")

# Run the function
export_cloud_checkpoint_vbm()