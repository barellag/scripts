import xml.etree.ElementTree as ET

# Specify the file path to your XML file
xml_path=input('Enter points path: ')
file_path = xml_path+'points.xml'

# Load the XML file
tree = ET.parse(file_path)
root = tree.getroot()

# Extract points and their original positions
points = [(i, int(point.get('Num')), point) for i, point in enumerate(root.findall('Point'))]

# Sort points by Num ascending, and maintain the original order as secondary sort key
points.sort(key=lambda x: (x[1], x[0]))

# Update Num values to ensure no duplicates, taking care to keep the order
num_set = set()
for i, (index, num, point) in enumerate(points):
    while num in num_set:
        num += 1  # Increment Num to find a non-duplicate value
    num_set.add(num)
    point.set('Num', str(num))  # Set the new Num value

# Write the updated XML content back to the file or to a new file
tree.write(xml_path+'new_points.xml', encoding='utf-8', xml_declaration=True)