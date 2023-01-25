import requests
payload = {
    'ctl00$MainContent$signin$usernameField': 'michael_admin',
    'ctl00$MainContent$signin$passwordField': ''
}

with requests.Session() as s:
    p = s.post('https://pennmedialab.getconnect2.com/SignIn.aspx', data=payload)
    print(p)
    print()
    r = s.get('https://pennmedialab.getconnect2.com/Lease/Checkin.aspx?id=10750')
    print(r.text)



#href="javascript:WebForm_DoPostBackWithOptions(new WebForm_PostBackOptions("ctl00$MainContent$signin$showLocalLk", "", true, "", "", false, true))" https://stackoverflow.com/questions/37164675/clicking-button-with-requests