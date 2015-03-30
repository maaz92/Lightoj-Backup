#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''

Keywords: python, tools, lightoj ,algorithms, solution, download,

Copyright (C) 2003-2004 Free Software Foundation, Inc.


Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

    * Redistributions of source code must retain the above copyright notice,
      this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright notice,
      this list of conditions and the following disclaimer in the documentation
      and/or other materials provided with the distribution.
    * Neither the name of the Secret Labs AB nor the names of its contributors
      may be used to endorse or promote products derived from this software
      without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

'''
#Dependencies:
#mechanize
#beautifulsoup

import os
import sys
import getpass
import optparse

try:
    from BeautifulSoup import BeautifulSoup, SoupStrainer
except ImportError:
    print "beautifulSoup required but missing"
    sys.exit(1)
try:
    from mechanize import Browser
except ImportError:
    print "mechanize required but missing"
    sys.exit(1)
    
    
if __name__=="__main__":
    proxy = raw_input("Enter the Proxy for your connection or type '-1' (without quotes) if your connection does not require a proxy\n")
    
    #handle no proxy
    if proxy == "-1":
        proxy = ""

    #for determining file extensions fromm language
    FILE_EXTENSION = { "C": ".c" , "C++" : ".cpp", "JAVA" : ".java" , "PASCAL" : ".pas"}
    
    # create a browser object
    br = Browser()

    # add proxy support to browser
    if len(proxy) != 0: 
        protocol,proxy = options.proxy.split("://")
        br.set_proxies({protocol:proxy})
    
    # let browser fool robots.txt
    br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; \
              rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
    br.set_handle_robots(False)

    print "Enter your lightoj username :",
    username = raw_input()
    password = getpass.getpass()

    # authenticate the user
    print "Authenticating " + username
    br.open ("http://www.lightoj.com/login_main.php")
    br.select_form (nr=0)
    br["myuserid"] = username
    br["mypassword"] = password
    
    # remember me to avoid timeouts
    br.form.set_all_readonly(False)
    br.find_control("myrem").selected = True

    br.form.action = "http://www.lightoj.com/login_check.php"
    response = br.submit()
    
    verify = response.read()
    if (verify.find("Authentication failed!") != -1):
        print "Error authenticating - " + username
        exit(0)

    print 'authenticated'
    # grab the signed submissions list
    print "Grabbing siglist for " + username
    submissions = br.open("http://www.lightoj.com/volume_usersubmissions.php")
    br.select_form (nr=0)
    br["user_password"] = password
    br.form.action = "http://www.lightoj.com/volume_usersubmissions.php"
    response = br.submit()
    #submissions = br.open("http://www.lightoj.com/volume_usersubmissions.php")
    soup = BeautifulSoup(response)#submissions)
    #print soup
    table = soup.findAll("table", { "id" : "mytable3" })[0]
    ctr = 0
    sub_ids=[]
    languages=[]
    problems=[]
    for tr in table.findAll("tr"):
        ctr = ctr + 1
        if ctr > 1:
            if str(tr.findAll('td')[5])[50:-15].strip() == 'Accepted':
                sub_id = str(tr.findAll('a')[0])
                sub_id = sub_id[70:-10]
                sub_id = sub_id.strip()
                sub_ids.append(sub_id)
                languages.append(str(tr.findAll('td')[2])[19:-5].strip())
                problems.append(str(tr.findAll('td')[1])[100:-15].strip())

    dir = username+'_lightoj_accepted_solutions/'
    try:
        os.stat(dir)
    except:
        os.mkdir(dir)   
    for sub_id,language,problem in zip(sub_ids,languages,problems):
        print 'downloading sub_id ' + sub_id + "...."
        submission = br.open("http://www.lightoj.com/volume_showcode.php?sub_id="+sub_id)
        soup = BeautifulSoup(submission)
        solution = str(soup.findAll("textarea")[0])
        solution = BeautifulSoup(solution[74:-11], convertEntities=BeautifulSoup.XML_ENTITIES).contents[0]
        f = open(dir+problem+'-'+sub_id+FILE_EXTENSION[language],"w") 
        f.write(solution.strip())
        f.close()

    
    print 'imported all files'