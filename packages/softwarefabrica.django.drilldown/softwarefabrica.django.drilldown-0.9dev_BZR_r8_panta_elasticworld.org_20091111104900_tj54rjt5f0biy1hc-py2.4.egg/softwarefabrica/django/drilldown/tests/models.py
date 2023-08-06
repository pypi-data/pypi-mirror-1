from django.db import models
from django.contrib.auth.models import User, Group, AnonymousUser

from softwarefabrica.django.common.models import *

class Author(CommonOwnedModel):
    first_name = models.CharField(max_length=50)
    last_name  = models.CharField(max_length=50)
    birth_date = models.DateField(blank=True, null=True, db_index=True)
    death_date = models.DateField(blank=True, null=True, db_index=True)

    def __unicode__(self):
        return u'%s, %s' % (self.last_name, self.first_name)

    class Meta:
        ordering = ['last_name', 'first_name', 'created']

    def get_absolute_url(self):
        return "/author/%s/" % self.pk

class Category(CommonOwnedModel):
    name       = models.CharField(max_length=50, db_index=True)
    slug       = models.SlugField(db_index=True, unique=True)

COVER_TYPE = (
    ('h',   'hard cover'),
    ('p',   'paperback'),
)

CONDITION_TYPE = (
    ('a',   'ancient'),
    ('u',   'used'),
    ('n',   'new'),
)

class Book(CommonOwnedModel):
    title      = models.CharField(max_length=200, db_index=True)
    slug       = models.SlugField(db_index=True, unique=True)
    excerpt    = models.TextField(blank=True)
    author     = models.ForeignKey(Author, db_index=True)
    year       = models.IntegerField(blank=True, default=2009)
    bought     = models.DateField(blank=True, null=True, db_index=True)
    keywords   = models.CharField(max_length=200, blank=True, db_index=True)
    cover      = models.CharField(max_length=2, choices=COVER_TYPE,
                                  blank=True, db_index=True)
    condition  = models.CharField(max_length=2, choices=CONDITION_TYPE,
                                  blank=False, db_index=True)

    categories = models.ManyToManyField(Category, db_index=True,
                                        null=True, blank=True)
    weight     = models.DecimalField(max_digits=9, decimal_places=3, blank=True, null=True)

    def __unicode__(self):
        return u'%s' % self.title

    class Meta:
        ordering = ['title', 'created', 'uuid',]

    class SFApp:
        drilldown_fields = ('title', 'desc', 'slug', 'author', 'year', 'bought',
                            'keywords', 'cover', 'condition', 'categories',
                            'weight',
                            'active',
                            'createdby', 'created', 'modifiedby', 'modified',)

    def get_absolute_url(self):
        return "/book/%s/" % self.pk
