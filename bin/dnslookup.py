"""
Copyright 2017-2020 Arnold Holzel

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
##################################################################
# Author        : Arnold Holzel
# Creation date : 2020-01-27 
# Description   : Splunk custom DNS lookup command. With this you can do
#               just about every type of DNS lookup and also filter for specific
#               sub-records. i.e. Just the SPF TXT record.                
#
# Version history
# Date          Version     Author      Type    Description
# 2020-01-27    1.0.0       Arnold              Initial version
# 2020-01-30    1.1.0       Arnold      [ADD]   Option to do a "SPF-walk", this will follow redirects and includes and will 
#                                               add an extra field 'spf_full' in the results with the full spf record.
# 2020-01-30    1.1.1       Arnold      [FIX]   If no record was provided the error handle didn't go well.
#
##################################################################
import splunk.Intersplunk
import re
from dns import resolver,reversename
import socket

def is_valid_ipv4_address(address):
    try:
        socket.inet_pton(socket.AF_INET, address)
    except AttributeError:  
        try:
            socket.inet_aton(address)
        except socket.error:
            return False
        return address.count('.') == 3
    except socket.error:  # not a valid address
        return False

    return True

def is_valid_ipv6_address(address):
    try:
        socket.inet_pton(socket.AF_INET6, address)
    except socket.error:  # not a valid address
        return False
    return True
 
def get_sub_record(answer,sub_record):
    p           = re.compile(".*" + sub_record + ".*", re.IGNORECASE)
    match       = p.match(str(answer))
    
    if match != None:
        return_subrecord = match.group()
    else:
        return_subrecord = None
        
    return return_subrecord

def get_full_spf(start_record,full_spf=[]):
    start_record = start_record.replace('" "','')
    
    if 'include' in start_record or 'redirect' in start_record:
        # we have a record that we need to following
        p           = re.compile('(?:include:|redirect=)[^\s\"]*', re.IGNORECASE)
        match       = p.findall(start_record)
        #print(f'match: {match}')
        for redirect_include in match:
            redirect_include    = redirect_include.replace('include:','')
            redirect_include    = redirect_include.replace('redirect=','')
            
            results  = resolver.query(redirect_include,'TXT')
            
            for result in results:
                tmp  = get_sub_record(result,'SPF')

                if 'include' in str(tmp) or 'redirect' in str(tmp):
                    get_full_spf(tmp,full_spf)
                else:
                    if tmp is not None:
                        full_spf.append(tmp)
    else:
        full_spf.append(start_record)
        
    return full_spf
    
def main():
    results = []
    output_results = []
    
    keywords,options = splunk.Intersplunk.getKeywordsAndOptions()
    results,dummyresults,settings = splunk.Intersplunk.getOrganizedResults()
    
    if 'field' not in options:
        output_result = splunk.Intersplunk.generateErrorResults("Usage: dnslookup field=<field-to-lookup> [[r=<dns-record-to-get>] [sr=<sub-record-to-get>]]")
        splunk.Intersplunk.outputResults(output_result)
        exit(0)
        
    field       = options.get('field', None)
    record      = options.get('r', None)
    sub_record  = options.get('sr', None)
    
    try:
        for result in results:
            full_spf = []
            if field in list(result.keys()):
                try:
                    # try to do a DNS lookup for the provided domain/ip
                    if record is None or record.lower() == 'ptr':
                        # if no record is specified or a PTR is requested, check if we are dealing with an IP
                        if is_valid_ipv4_address(result[field]):
                            is_ip           = True
                            search_record   = 'PTR'
                        elif is_valid_ipv6_address(result[field]):
                            is_ip           = True
                            search_record   = 'PTR'
                        else:
                            is_ip           = False
                            search_record   = 'A OR AAAA'
                            
                        if is_ip:
                            # we have a IP, do a reverse lookup and get the PTR record
                            addr        = reversename.from_address(result[field])
                            answers     = resolver.query(addr, 'PTR')
                        else:
                            # we have a fqdn/hostname so try to get the A and AAAA record 
                            try:
                                answers_A       = resolver.query(result[field], 'A')
                            except Exception as exception:
                                answers_A       = 'exception'
                                pass
                                
                            try:
                                answers_AAAA    = resolver.query(result[field], 'AAAA')
                            except Exception as exception:
                                answers_AAAA    = 'exception'
                                pass
                                
                            answers     = []
                            
                            if answers_A != 'exception':
                                for a in answers_A:
                                    answers.append(a)
                            
                            if answers_AAAA != 'exception':
                                for aaaa in answers_AAAA:
                                    answers.append(aaaa)
                    else:
                        # for all other records just do a lookup for it.
                        answers         = resolver.query(result[field], record)
                except Exception as exception:
                    # catch the exeption and give that back (NXDOMAIN/NoAnswer/....)
                    result['dnslookup'] = str(type(exception).__name__)
                else:
                    # process the provided answers and look for the requested sub-record if it is requested
                    for rdata in answers:
                        if sub_record is None:
                            # no subrecord is requested contatenate all the answers with a "marker" between them 
                            # this way we can later split them to return a multi value field 
                            if 'dnslookup' in result:
                                tmp                 = str(result['dnslookup']) + '\|/' + str(rdata)
                                result['dnslookup'] = tmp
                            else:
                                result['dnslookup'] = rdata
                        elif sub_record == 'spf-full':
                            tmp                 = get_sub_record(rdata,'SPF')
                            
                            if tmp is not None:
                                result['spf_full']  = get_full_spf(tmp,full_spf)
                                result['dnslookup'] = tmp
                        else:
                            if 'dnslookup' in result:
                                tmp                 = get_sub_record(rdata,sub_record)
                                
                                if tmp is not None:
                                    tmp             = str(result['dnslookup']) + '\|/' + str(tmp)
                                else:
                                    tmp             = str(result['dnslookup'])
                                    
                                result['dnslookup'] = tmp
                            else:
                                tmp                 = get_sub_record(rdata,sub_record)
                                
                                if tmp is not None:
                                    result['dnslookup'] = tmp
            
            if 'dnslookup' not in result:
                if 'search_record' in locals():
                    error_record    = search_record
                else:
                    error_record    = record
                    
                if sub_record is None:
                    result['dnslookup'] = '\'' + str(error_record).upper() + '\' record not found'
                else:
                    result['dnslookup'] = '\'' + str(error_record).upper() + '\'' + ' record with sub record \'' + str(sub_record).upper() + '\' not found'
                    
            if "\|/" in str(result['dnslookup']):
                result['dnslookup'] = result['dnslookup'].split("\|/")
                
            output_results.append(result)

    except Exception:
        import traceback
        stack =  traceback.format_exc()
        output_results = splunk.Intersplunk.generateErrorResults("Error : Traceback: " + str(stack))

    splunk.Intersplunk.outputResults(output_results)

if __name__ == "__main__":
    main()

