from django.db import models


STATUS = (
    ('known', 'Known'),  #first value value to be stored, 2nd human readable
    ('novel', 'Novel')
    )




class Tags(models.Model):
#    TAG_CHOICES = (
#    ('organism', 'Organism'),
#    ('gene_name', 'Gene name')
#    ('hgnc_name', 'HGNC name')
#    ('GO', 'GO description')
#    ('pfam', 'Pfam description')
#    ('gstatus', 'Gene status')
  
#    )
    tag_type = models.CharField(max_length=50)
    tag_acc = models.CharField(max_length=50, blank=True)
    tag_name = models.CharField(max_length=300)
    tag_details = models.CharField(max_length=300, blank=True)
    
    def __unicode__(self):
        return '%s; %s; %s' %(self.tag_type, self.tag_acc, self.tag_name)
#    class Admin:
#        list_display = ('tag_type', 'tag_acc', 'tag_name','tag_details')
    class Meta:
        unique_together = (('tag_type', 'tag_name', 'tag_acc'),)
        
class Gene(models.Model):
    
    descript = models.CharField(max_length=200)
    orgn = models.CharField(max_length=100)
    tags =  models.ManyToManyField(Tags, through='Genetag')
    
    
    def __unicode__(self):
        return '%s; %s' %(self.descript, self.orgn)

    class Meta:
        unique_together = (('orgn', 'descript',),)      
        
class Genetag(models.Model):
    gene = models.ForeignKey(Gene)
    tags = models.ForeignKey(Tags)
    def __unicode__(self):
        return '%s; %s' %(self.gene, self.tags)
   
    class Meta:
        unique_together = (('gene', 'tags'),)

class Seq(models.Model):
    SEQ_CHOICES = (
    ('dna', 'DNA'),
    ('protein', 'Protein')
    )
    gene = models.ForeignKey(Gene)
    seq_type = models.CharField(max_length=20, choices=SEQ_CHOICES)
    sequence = models.TextField()
    
    def __unicode__(self):
        return '%s; %s; %s; %s' %(self.gene, self.gene.orgn, self.seq_type, self.sequence)



class Entrez(models.Model):
    sprot = models.CharField(max_length=50)
    tags = models.ForeignKey(Tags)
    def __unicode__(self):
        return '%s; %s;' %(self.sprot, self.tags)
   

#should not be modified
class GO(models.Model):
    pid1 = models.IntegerField()
    pid2 = models.IntegerField()
    
    

    
    
    
    
    
    
    
    
    
from django.db import models

# Create your models here.
