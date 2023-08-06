from django.shortcuts import get_object_or_404, render_to_response
from tagbase.gutentag.models import Gene, Tags, Genetag, Seq, Entrez, GO
from django.template import Context, loader
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.core.mail import EmailMessage
from django.conf import settings
from django.db.models import Q
from random import randint
import subprocess
import blast
import log
import os
import glob
import thread


def display_tag():
    '''
    groups tags data so they may be displayed 
    '''
    gname_list=[]
    cdd_list=[]
    org_list=[]
    d={}
    s = Genetag.objects.select_related().all()
    for genetagobj in s:
        tag_obj = genetagobj.tags
        tag_type = tag_obj.tag_type
        tag_name = tag_obj.tag_name
#        print '%s' %repr(tag_type)
	if tag_type == 'gene_name' and tag_name not in gname_list:
	    gname_list.append(tag_name)
        if tag_type == 'cdd' and tag_name not in cdd_list:
            cdd_list.append(tag_name)
        if tag_type == 'organism' and tag_name not in org_list:
            org_list.append(tag_name)
    
    gname_list.sort()
    cdd_list.sort()
    org_list.sort()
    d['gname']= gname_list
    d['cdd']= cdd_list
    d['organism']= org_list
    return d
    
    
def co(list):
    '''
    Returns maximum and minimum counts (for generating tags clouds)
    '''
    num_counts = {}
    for i in list:
        num_counts[i] = num_counts.get(i, 0) + 1
    maxi = max(num_counts, key=lambda x: num_counts[x])
    mini = min(num_counts, key=lambda x: num_counts[x])
    return num_counts, maxi, mini
    
def process_cloud_tag(tag_type):
    ''' distribution algo n tags to b bucket, where b represents
    font size. '''
    tagNameList = []
    emptylist = []
    if tag_type == 'user':
        gtagObj = Genetag.objects.exclude( Q(tags__tag_type='cdd') |\
        Q(tags__tag_type='go') | Q(tags__tag_type='gene_name')  |\
	Q(tags__tag_type='organism'))   
	#print 'gtagObj=%s' %gtagObj
	if gtagObj.count() == 0:
	    return emptylist
	for gtag in gtagObj:
            tagNameList.append(gtag.tags.tag_name)
	    tagNameList.append(gtag.tags.tag_type)
	    tagNameList.append(gtag.tags.tag_acc)
	    tagNameList.append(gtag.tags.tag_details)
    else:    
    	gtagObj = Genetag.objects.filter(tags__tag_type=tag_type)
    	if gtagObj.count() == 0:
	    return emptylist
    	for gtag in gtagObj:
        	tagNameList.append(gtag.tags.tag_name)
    num_counts, maxi, mini = co(tagNameList)
    print num_counts
    nbr_of_buckets = 8
    base_font_size = 11
    tresholds = []
    delta = (float(num_counts[maxi]) - float(num_counts[mini])) / (float(nbr_of_buckets))
    # set a treshold for all buckets
    for i in range(nbr_of_buckets):
        tresh_value =  float(num_counts[mini]) + (i+1) * delta
        tresholds.append(tresh_value)
    # set font size for tags (per bucket)
    cloudList = []
    for name in num_counts.keys():
        l = []
        count = num_counts[name]
        font_set_flag = False
        for bucket in range(nbr_of_buckets):
            if font_set_flag == False:
                if (count <= tresholds[bucket]):
                    font_size = base_font_size + bucket * 2
                    l = [name, count, font_size]
                    cloudList.append(l)
		    font_set_flag = True
    return cloudList
 
      
def main(request):
    d = display_tag()
    gobj = Gene.objects.all()
#    gene_info  = display_gene_info()
    cddCloud = process_cloud_tag('cdd')
    gnameCloud = process_cloud_tag('gene_name')
    userCloud = process_cloud_tag('user')
    tag_orgn = Tags.objects.filter(tag_type='organism')
    
        
    return render_to_response('gutentag/main.html', {'gnamelist':d['gname'],  
                     'cddlist':d['cdd'],'genelist':gobj, 'orgn':d['organism'],
	'cddCloud':cddCloud, 'gnameCloud':gnameCloud, 'userCloud':userCloud, 
	 'tag_orgn':tag_orgn, 'blastdb':settings.BLASTDB, 'dbname':settings.DBNAME })

def getUser():
    userList = []
    tagObj = Tags.objects.exclude( Q(tag_type='cdd') |\
        Q(tag_type='go') | Q(tag_type='gene_name')  |\
	Q(tag_type='organism'))   
    print 'tagObj=%s' %tagObj
    	
    for tag in tagObj:
        templ=[]
        templ.append(tag.tag_type)
        templ.append(tag.tag_name)
        templ.append(tag.tag_acc)
        templ.append(tag.tag_details)
        entry = ','.join(templ)
        userList.append(entry)
    print 'userList=%s' %userList
    return userList
    
def org_tag():
    '''
    Retrieve all organisms listed in tags table
    '''
    tag_orgn = Tags.objects.filter(tag_type='organism')
    return tag_orgn

def add(request):
    tag_orgn = org_tag()
    userList = getUser()
    return render_to_response('gutentag/add.html', {'tag_orgn':tag_orgn,
	'userList':userList, 'blastdb':settings.BLASTDB,'dbname':settings.DBNAME})
    

def retrievecdd(data):
    cdd_qs = Seq.objects.filter(gene__genetag__tags__tag_type='cdd', 
    gene__genetag__tags__tag_name__iexact=data)
    cdd_qs = set(cdd_qs)
    return cdd_qs


def retrieveGname(data):
    gname_qs = Seq.objects.filter(gene__genetag__tags__tag_type='gene_name', 
    gene__genetag__tags__tag_name__iexact=data)
    gname_qs = set(gname_qs)
    return gname_qs


def retrieveSearch(data):
    s_qs = Seq.objects.filter(gene__descript__icontains=data) | \
        Seq.objects.filter(gene__genetag__tags__tag_name__icontains=data)  | \
        Seq.objects.filter(gene__genetag__tags__tag_details__icontains=data)
    s_qs = set(s_qs)
    return s_qs


def retrieveUser(data):
    user_qs1 = Seq.objects.exclude(Q(gene__genetag__tags__tag_type='cdd')| 
			      Q(gene__genetag__tags__tag_type='go')|
			      Q(gene__genetag__tags__tag_type='gene_name')|
			      Q(gene__genetag__tags__tag_type='organism'))      
    user_qs = user_qs1.filter(Q(gene__genetag__tags__tag_name__iexact=data)| 
	                   Q(gene__genetag__tags__tag_details__iexact=data)| 
	                      Q(gene__genetag__tags__tag_type__iexact=data)|
			      Q(gene__genetag__tags__tag_acc__iexact=data))
    user_qs = set(user_qs)			      
    return user_qs




def retrieveHeader(data):
    header_qs = Seq.objects.filter(gene__descript__iexact=data)
    return header_qs


def retrieveOrg(data):
    org_qs = Seq.objects.filter(gene__genetag__tags__tag_type='organism', 
                              gene__genetag__tags__tag_name__iexact=data)
    org_qs = set(org_qs)
    return org_qs    

    
def tagCloudSearch(request, tag_name, tag_type):
    if tag_type == 'cdd':
        gs = retrievecdd(tag_name)
    if tag_type == 'user':
        gs = retrieveUser(tag_name) 
    if tag_type == 'gname':
        gs = retrieveGname(tag_name)
    if tag_type == 'header':
        gs = retrieveHeader(tag_name)
    if tag_type == 'org':
        gs = retrieveOrg(tag_name)
   
    cstr = '%s' %(tag_name)
    count = len(gs)
    request.session['gs'] = gs
    return render_to_response('gutentag/display.html', {'cstr': cstr, 
                                      'new_queryset':gs, 'count':count})
                                      
                                      
def findIntersection(gsList):
    for i in range(len(gsList)):
        if i == len(gsList) - 1:
            return gsList[i]
        if i == 0:
            res = []
        for obj in gsList[i]:
            if obj in gsList[i+1]:
                res.append(obj)
        gsList[i+1] = res    
	res = 0  

def mainSearch(request):
    gsList=[]
    tagList = []
    final_gs = []
    hold = Gene.objects.none()
    content = request.GET['content']
    if content != '':
        gs = retrieveSearch(content)
        gsList.append(gs)
        tagList.append('%s in Search All' % content)
    header = request.GET['header']
    if header != 'empty':
        print 'header=%s' %header
        gs = retrieveHeader(header)
        gsList.append(gs)
        tagList.append('%s in FASTA Headers' % header)
    if settings.BLASTDB != '':
        gname = request.GET['gname']
        if gname != 'empty':
            gs = retrieveGname(gname)
            gsList.append(gs)
            tagList.append('%s in Gene Names' % gname)
        cdd = request.GET['cdd']
        if cdd != 'empty':
            gs = retrievecdd(cdd)
            gsList.append(gs)
            tagList.append('%s in cdd Names' % cdd)
    org = request.GET['org']
    if org != 'empty':
        gs = retrieveOrg(org)
        gsList.append(gs)
        tagList.append('%s in Organisms' % org)
    cstr = ' AND '.join(tagList)

    try:
        if len(gsList) > 2:
            return render_to_response('gutentag/error.html', {'message':'Only select two combinations at a time!'})
        if len(gsList) == 2:
            print "gsList%s=" %gsList
            final_gs = findIntersection(gsList)
            print 'final_gs=%s' %final_gs
        
        if len(gsList) == 1:
	    final_gs = gsList[0]       
	count = len(final_gs)	                

	   
	if len(final_gs) == 0: 
            raise LookupError
            
    except LookupError:
    
        return render_to_response('gutentag/noSeq.html', {'cstr': cstr})
    else:

        request.session['gs'] = final_gs
        return render_to_response('gutentag/display.html', {'cstr': cstr, 
	                             'new_queryset':final_gs, 'count':count})
    

def getSeq(request):
    seqstr = ''
    seqObjList = request.session['gs']
    for seqob in seqObjList:
        seqstr = seqstr + seqob.sequence + '\n\n'
    return HttpResponse(seqstr, mimetype="text/plain")     
          
  #  return render_to_response('homolodb/seq.html', {'seqObjList':seqObjList})         

def getTags(request, gene_id):
    TagsQs = Tags.objects.filter(genetag__gene__id=gene_id)
    return render_to_response('gutentag/displayTags.html', {'tag_qs': TagsQs})   
    
def getThisSeq(request, seq_id):
    seqobj = Seq.objects.get(id=seq_id)
    seqstr = seqobj.sequence
    return HttpResponse(seqstr, mimetype="text/plain")      
    
def displayGo(GOlist):
    go_list=[]
    for obj in GOlist:
        pid2 = obj.pid2
        child = list(Tags.objects.filter(id = pid2))[0]
        count =  Genetag.objects.filter(tags=pid2).count()
        tup = (child, count)
        go_list.append(tup)
    return go_list
        
        
def go(request, go_id):
    '''
    display go terms
    todo:
    if go_id = 0
    then get acc, name from tags and count of genetags
    of 3 super parents
    
    if go_id is something else
    then go to go table
    '''
    go_id = str(go_id)
    if go_id == '0':
        print 'go = 0'
        super1 = Tags.objects.get(id=8520) 
        super2 = Tags.objects.get(id=9438) 
        super3 = Tags.objects.get(id=10219)
        print super1
        c1 = Genetag.objects.filter(tags=8520).count()
        c2 = Genetag.objects.filter(tags=9438).count()
        c3 = Genetag.objects.filter(tags=10219).count() 
        go_list = [(super1,c1), (super2, c2), (super3, c3)]
        print go_list
    else:
        GOlist = list(GO.objects.filter(pid1=go_id))    
        go_list = displayGo(GOlist)
    return render_to_response('gutentag/gobrowser.html', {'go_list':go_list, 
                             'dbname':settings.DBNAME, 'blastdb':settings.BLASTDB})

def goSeq(request, go_id):
    seqstr = ''
    seqObjList = Seq.objects.filter(gene__genetag__tags__id=go_id)
    #return render_to_response('gutentag/seq.html', {'seqObjList':seqObjList}) 
    for seqob in seqObjList:
        seqstr = seqstr + seqob.sequence + '\n\n'
    return HttpResponse(seqstr, mimetype="text/plain")     
        
    
def handle_uploaded_file(request, f):

    if isinstance(f, unicode):
        request.session['fasta_file'] = str(f)
    else:
        request.session['fasta_file'] = str(f.read())

    

def seq_generator(fasta):
        header = ''
        seq = []
        for line in fasta:
            line = line.strip()
            if line:
                if line[0]=='>':
                    if seq:
                        yield header, ''.join(seq)
                    header = line[1:]
                    seq = []
                else:
                    seq.append(line)
        if header and seq:
            yield header, ''.join(seq)



def load_new_seq(request, org, seq_type, taglist, usertag):
    tag = None
    utag = None
    
    if usertag != 'empty':
        tagtok = usertag.split(',')
        print 'tagtok=%s' %tagtok
        utag = Tags.objects.get(tag_type=tagtok[0], tag_name=tagtok[1],
		tag_acc=tagtok[2], tag_details=tagtok[3]) 
    if taglist != []:
        tag = Tags.objects.create(tag_type=taglist[0][0],tag_name=taglist[0][1],
	tag_acc=taglist[0][2], tag_details=taglist[0][3])
    print 'loading sequences into gene table'

    fasta = request.session['fasta_file']
    fastalist = fasta.split('\n')
    print 'fasta%s' %fasta
    for header, seq in seq_generator(fastalist):
        #find all gaps in header and replace with _
        header = header.replace(' ','_')
        header = header.replace('-','_')
        print 'header=%s' %header
	print 'seq=%s' %seq
        print 'org=%s' %org
        whole = '>' + header + '\n' + seq
        checkdup = Gene.objects.filter(descript=header, orgn=org)
        print 'checkdup=%s' % checkdup
        if str(checkdup) != '[]':
            return 'error dup'
        g = Gene.objects.create(descript=header, orgn=org)
        # create entries in org tag
        t = Tags.objects.get(tag_type='organism', tag_name=org) 
        Genetag.objects.create(tags_id=t.id, gene_id=g.id)
        if tag != None:
            Genetag.objects.create(tags_id=tag.id, gene_id=g.id)
            print 'newtag added tagid=%s geneid=%s' %(tag.id, g.id)
        if utag != None:    
            Genetag.objects.create(tags_id=utag.id, gene_id=g.id)
            print 'newgenetag added tagid=%s geneid=%s' %(utag.id, g.id)
       # g = Gene.objects.get(descript=header, orgn=org)
       # gid = g.id
       # print 'gene id%s' %gid
        s = g.seq_set.create(sequence=whole, seq_type=seq_type, gene=g.id)
  

def runBlastcl3(request, seq_type):
    log.debug('running blast')
    if seq_type == 'dna':
        program = 'blastx'
    else:
        program = 'blastp' 
    fasta_input = request.session['fasta_file']
    retcode, stdout_value = blast.runBlastcl3 (program, fasta_input)
    request.session['annot_blastout'] = stdout_value
    return retcode

        
        
def parseBlastHits(request, org, evalue):
    createdTags = ''
    blast = request.session['annot_blastout']
    blast = blast.split('\n')
    for line in blast:
        if '<BlastOutput_query-def>' in line:
            descript = line.split('<BlastOutput_query-def>')[1].split('</')[0]
            descript = descript.replace(' ','_')
            descript = descript.replace('-','_')
#           print descript
            # get the gene id from blast query header
            try:
                gobj = Gene.objects.get(descript=descript, orgn=org)
            except AssertionError:
                print 'Fasta headers are not unique. Another entry in database with same description and orgn.'
            except ObjectDoesNotExist:
                print 'Sequence entry does not exist'
	    gid = gobj.id
        if '<Hit_num>1</Hit_num>' in line:
            hitYes = 1
        if '<Hit_accession>' in line and hitYes:
            sprotacc = line.split('<Hit_accession>')[1].split('</')[0]  
	if '<Hsp_evalue>' in line and hitYes:
	    e = float(line.split('<Hsp_evalue>')[1].split('</')[0])
	    if e > evalue:
                log.debug('Eval less than user cut-off in SP search')
	        hitYes = 0
	    else:  
	        hitYes = 0
                # use swissprot accession to get tag ids from entrez table 
    	        eobj_list = Entrez.objects.filter(sprot=sprotacc)
	        for eobj in eobj_list:
	            tid = eobj.tags_id
	            print 'tid=%s' %tid
	            try:
	                tobj = Tags.objects.get(id=tid)
	            except:
		        continue   
		    tag_acc = tobj.tag_acc
	            tag_name = tobj.tag_name
	            # add each tag id into genetag table
	            Genetag.objects.create(tags_id=tid, gene_id=gid)

	            log.debug('%s\t%s\t%s\t%s' %(tid, tag_acc, tag_name, sprotacc))
           

	if 'No hits found' in line:
            log.debug('No significant similarity in Swissport for %s' %descript)
	    print 'No significant similarity in Swissprot for %s' %descript  

   
    
def sendMail(mail):
    email = EmailMessage('Tags have been generated', 'Tags have been generated. You can now browse using these tags. \nTags may include gene name, conserved domains and GO nodes. Gene names and conserved domains have tag clouds for easy browsing.', 'from@example.com', [mail])       
    email.send()
    

def runBlastcl3CDD(request):
    log.debug('running CDD blast')
    fasta_input = request.session['fasta_file']    
    retcode, stdout_value = blast.runBlastcl3CDD(fasta_input)
    request.session['annot_blastout'] = stdout_value
    return retcode

        
def parseCDDBlastHits(request, org, evalue):
 
    info=None
    log.debug('parsing CDD results')
    blast = request.session['annot_blastout']

 
    blast = blast.split('\n')
    for line in blast:
        if 'Query= ' in line:
            hitYes=0
            eYes=0
            descript = line.strip().split('Query= ')[1]
            descript = descript.replace(' ','_')
            descript = descript.replace('-','_')
#           print descript
            # get the gene id from blast query header
            try:
                gobj = Gene.objects.get(descript__istartswith=descript, orgn=org)
            except AssertionError:
                log.debug('Fasta headers are not unique. Another entry in database with same description and orgn.')
            except ObjectDoesNotExist:
                log.debug('Sequence entry does not exist')
                
	    gid = gobj.id
        if 'gnl|CDD|' in line and hitYes==0:
            hitYes = 1
            log.debug('found hit')
            info = line.split()[0]
        if info:
            if info in line:
                info = None
                cddacc= line.split()[1].strip(',')
                cddname= line.split()[2].strip(',')
                cdddet= line.split()[3].strip(',')
        if 'Expect = ' in line and eYes==0:
	    eYes=1
	    e = float(line.strip().split('Expect = ')[1].split(',')[0])                
            log.debug('top eval of CDD search: %s' %str(e))
            if e <= evalue:
                log.debug('e less than user value for CDD search')
                print 'e less than user value'
	        try:
	            tag = Tags.objects.get(tag_type='cdd',tag_name=cddname,
	              tag_acc=cddacc, tag_details=cdddet)
	        except:
	            tag = Tags.objects.create(tag_type='cdd',tag_name=cddname,
	            tag_acc=cddacc, tag_details=cdddet)
	        Genetag.objects.create(tags_id=tag.id, gene_id=gid)
	        log.debug('%s\t%s\t%s\t%s' %(tag.id, cddname, cddacc, cdddet))
            else:
                log.debug('Evalue is greater than user values in CDD search: %s' %e)
	if 'No hits found' in line:
            log.debug('No significant similarity in CDD for %s' %descript)



def annotate(request, org, mail, seq_type, evalue):
    retcode = runBlastcl3(request, seq_type)
    if retcode == 0:  # successful return
        # parse top hits
        log.debug('Successful search')
        parseBlastHits(request, org, evalue)
        if seq_type == 'protein':
            runBlastcl3CDD(request)
            if retcode == 0:
                parseCDDBlastHits(request, org, evalue)
                log.debug('Finished both BLASTs')
                
                sendMail(mail)
	else:
	    sendMail(mail)


    tag_orgn = org_tag()
    userList = getUser()
    


def upload(request):
    tag_orgn = org_tag()
    userList = getUser()
    taglist=[]
    usertag = 'empty'
    doannotations = None
    addtag = None
    seq = request.POST['seqtext']
    if request.FILES == {} and seq == '':
        return render_to_response('gutentag/add.html', {'tag_orgn':tag_orgn,
        'userList':userList, 'dbname':settings.DBNAME, 'blastdb':settings.BLASTDB, 'error_message':'ERROR...No sequence data'})
    if seq != '':
        handle_uploaded_file(request, seq)
    else:     
        f = request.FILES['upfile']
        handle_uploaded_file(request, f)
    seq_type = str(request.POST['sequence'])
    org = request.POST['orgselect']
    neworg = request.POST['neworg']
    neworg = neworg.replace(' ','_')
    neworg = neworg.replace('-','_')
    usertag = request.POST['usertags']
    print 'usertag%s' %usertag
    
    try:
        doannotations = request.POST['annot']
        email = request.POST['email']
        evalue = float(request.POST['evalue'])
    except:
        pass    
    try:
        addtag = request.POST['newtag']
        print 'addtag%s' %addtag 
    except:
        pass
   
    if org =='empty' and neworg =='':
        return render_to_response('gutentag/add.html', {'tag_orgn':tag_orgn,
        'userList':userList, 'dbname':settings.DBNAME, 'blastdb':settings.BLASTDB, 'error_message':'ERROR...Sequence/s must be associated with an organism'})
               
    if org == 'empty':
        Tags.objects.create(tag_type='organism', tag_name=neworg)
        org = neworg
    print 'addtag%s' %addtag    
    if addtag:
        newtagtype = request.POST['newtagtype']
        newtagtype = newtagtype.replace(' ','_')
        newtagtype = newtagtype.replace('-','_')
        newtagtype = newtagtype.replace('.','_')
        newtagname = request.POST['newtagname']
        newtagname = newtagname.replace(' ','_')
        newtagname = newtagname.replace('-','_')
        newtagname = newtagname.replace('.','_')
        if newtagtype == newtagname:
            return render_to_response('gutentag/add.html', {'tag_orgn':tag_orgn,
        'userList':userList, 'dbname':settings.DBNAME, 'blastdb':settings.BLASTDB, 'error_message':'ERROR...Tag name and tag type cannot be identical'})
 
#        newtagacc = request.POST['newtagacc']
#        newtagacc = newtagacc.replace(' ','_')
#        newtagdet = request.POST['newtagdet']
#        newtagdet = newtagdet.replace(' ','_')
#        taglist.append([newtagtype, newtagname, newtagacc, newtagdet])
        taglist.append([newtagtype, newtagname, '', ''])
        print 'taglist %s' %taglist
    if doannotations:
        checkerror = load_new_seq(request, org, seq_type, taglist, usertag)
        if checkerror == 'error dup':
            return render_to_response('gutentag/add.html', {'tag_orgn':tag_orgn,
        'userList':userList, 'dbname':settings.DBNAME, 'blastdb':settings.BLASTDB, 'error_message':'ERROR...Sequence name and organism already present in database'})
       
	log.debug('started annotation of new sequences')
        thread.start_new_thread(annotate, (request, org, email, seq_type, evalue))
        
        return render_to_response('gutentag/annotate.html', {'email':email})
   
        
    checkerror = load_new_seq(request, org, seq_type, taglist, usertag)
    if checkerror == 'error dup':
        return render_to_response('gutentag/add.html', {'tag_orgn':tag_orgn,
        'userList':userList, 'dbname':settings.DBNAME, 'blastdb':settings.BLASTDB, 'error_message':'ERROR...Sequence name and organism already present in database'})

    return render_to_response('gutentag/seqLoaded.html')


    
       

def doblast(request):
    return render_to_response('gutentag/blast.html', {'dbname':settings.DBNAME, 'blastdb':settings.BLASTDB})

    
def makeBlastInput(key, seqtype):
    allseq=''
    log.debug(seqtype)
    seqs = Seq.objects.filter(seq_type=seqtype)
    
    print 'seqs=%s'%seqs
    for seq in seqs:
        allseq = allseq + seq.sequence + '\n'
    blastin_location = settings.BLASTDB + r'/%sblastdb' % key 
    blastf = open(blastin_location, 'w')  
    blastf.write(allseq)
    blastf.close()
    return blastin_location

    
def runBlast(key, db, program, seq):
    results = blast.runBlastAll(db, program, seq)
    return results
    
    
def blastSearch(request):
    key = randint (0,100)
    out = None
    seq = request.GET['seqtext']
    seq = str(seq)
    seqtype = str(request.GET['sequence'])
    program = request.GET['program']
   
   
    if program == 'empty': 
        return render_to_response('gutentag/add.html', {'error_message':"Choose a sequence type"})
    inputFile = makeBlastInput(key, seqtype)
    db = settings.BLASTDB + r'/%s' % key
    retcode = blast.makeNewDB(inputFile, seqtype, db)
    if retcode == 0:
        results = runBlast(key, db, program, seq)
        log.debug('finished BLAST')
	# clear the database files
        files = settings.BLASTDB + r"/%s.*" % key
	filenames = glob.glob(files)
	for each in filenames:
	    os.remove(each)
	os.remove(settings.BLASTDB + r'/%sblastdb' % key )
        log.debug('Removed temp BLAST files')
	return HttpResponse(results, mimetype="text/plain")    
    else:
        return render_to_response('homolodb/error.html') 
    
    
