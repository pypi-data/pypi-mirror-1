from django.db import models
from softwarefabrica.django.utils.IPv4MaskedAddressField import IPv4MaskedAddressField

class IPAddressData(models.Model):
    ip         = IPv4MaskedAddressField()

    def __unicode__(self):
        return str(self.ip)

class Author(models.Model):
    name       = models.CharField(max_length=50)
    last_name  = models.CharField(max_length=50)
    birth_year = models.IntegerField()
    active     = models.BooleanField(default=True)

    def __unicode__(self):
        return u'%s %s' % (self.name, self.last_name)

    class Meta:
        ordering = ['last_name', 'name']

    def get_absolute_url(self):
        return "/authors/%s/" % self.id

    def get_create_url(cls):
        return "/authors/new/"
    get_create_url = classmethod(get_create_url)

    def get_edit_url(self):
        return "/authors/%s/edit" % self.id

    def get_list_url(cls):
        return "/authors/"
    get_list_url = classmethod(get_list_url)

class Book(models.Model):
    title      = models.CharField(max_length=200)
    isbn       = models.CharField(max_length=32, blank=True)
    author     = models.ForeignKey(Author, null=True)
    active     = models.BooleanField(default=True)

    def __unicode__(self):
        if self.author:
            return u'%s (%s)' % (self.title, self.author)
        return u'%s' % self.title

    class Meta:
        ordering = ['title']

class BookRent(models.Model):
    book       = models.ForeignKey(Book)
    when       = models.DateTimeField()

    def __unicode__(self):
        return u'%s - %s' % (self.book, self.when)

    class Meta:
        ordering = ['-when', 'book', '-id']
