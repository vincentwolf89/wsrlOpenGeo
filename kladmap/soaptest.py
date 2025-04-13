import requests

url = "https://rivierenland.relaticsonline.com/DataExchange.asmx?"

payload = "<SOAP-ENV:Envelope xmlns:SOAP-ENV=\"http://www.w3.org/2003/05/soap-envelope\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xmlns:xsd=\"http://www.w3.org/2001/XMLSchema\">\r\n\t<SOAP-ENV:Body>\r\n\t\t<GetResult xmlns=\"http://www.relatics.com/\">\r\n\t\t\t<Operation>TestToegangPictoKlanteisID</Operation>\r\n\t\t\t<Identification>\r\n\t\t\t\t<Identification>\r\n\t\t\t\t\t<!-- Workspace ID SAFE -->\r\n\t\t\t\t\t<Workspace>060b559f-f6c0-4fcb-8990-aa02a7a0f44f</Workspace>\r\n\t\t\t\t</Identification>\r\n\t\t\t</Identification>\r\n\t\t\t<Parameters> \r\n\t\t\t\t<Parameters>\r\n\t\t\t\t\t<Parameter Name=\"KlanteisID\" Value=\"KE_00542\"/>\r\n\t\t\t\t</Parameters>\r\n\t\t\t</Parameters> \r\n\t\t\t<!-- skip the Parameters part, in case there are no parameters. NB: avoid <Parameters/>  -->\r\n\t\t\t<Authentication>\r\n\t\t\t\t<Authentication>\r\n\t\t\t\t\t<Entrycode>69EE84714414EFC07A0E8525CACAA599</Entrycode>\r\n\t\t\t\t</Authentication>\r\n\t\t\t</Authentication>\r\n\t\t</GetResult>\r\n\t</SOAP-ENV:Body>\r\n</SOAP-ENV:Envelope>\r\n"
headers = {
  'Content-Type': 'text/xml; charset=utf-8',
  'Cookie': 'ASP.NET_SessionId=52ggzfywwbtjcohj5jczkfqk; SESSION_START_COOKIENAME_29C5C783-84D0-4D23-A8F0-F888A8C64C78=true'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
