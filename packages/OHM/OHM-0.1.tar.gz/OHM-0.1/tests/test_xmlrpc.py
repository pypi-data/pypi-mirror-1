from ohm.validators import XMLRPCConverter

def test_converter():
    conv = XMLRPCConverter()
    data = dict(a=1, b=2)
    serialized = conv.from_python(data)
    assert serialized == '''\
<object><value><struct>
<member>
<name>a</name>
<value><int>1</int></value>
</member>
<member>
<name>b</name>
<value><int>2</int></value>
</member>
</struct></value>
</object>'''
    new_data = conv.to_python(serialized)
    assert new_data == data
    
    
    
