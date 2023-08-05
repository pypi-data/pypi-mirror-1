import elementtree.ElementTree as ET

def record2xml(record):
  root = ET.Element('record')
  leader = ET.SubElement(root, 'leader')
  leader.text = record.leader

  for field in record.control_fields:
    field_el = ET.SubElement(root, 'controlfield')
    field_el.attrib['tag'] = field.tag
    field_el.text = field.value

  for field in record.data_fields:
    field_el = ET.SubElement(root, 'datafield')
    field_el.attrib['tag'] = field.tag
    field_el.attrib['ind1'] = field.indicator1
    field_el.attrib['ind2'] = field.indicator2

    for subfield in field.subfields:
      subfield_el = ET.SubElement(field_el, 'subfield')
      subfield_el.attrib['code'] = subfield.code
      subfield_el.text = subfield.value

  return ET.tostring(root)


